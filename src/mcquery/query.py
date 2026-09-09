#
# Copyright (c) 2017-2021 w-gao
#
import argparse
import logging
import re
import struct
import sys
import socket
import time
from contextlib import contextmanager
from random import randint
from typing import Generator


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.WARNING)


# constants
MC_QUERY_MAGIC = b'\xFE\xFD'
MC_QUERY_HANDSHAKE = b'\x09'
MC_QUERY_STATISTICS = b'\x00'

# RakNet magic for the unconnected ping, used as a warm-up fallback (see _unconnected_ping)
RAKNET_PING_MAGIC = b'\x00\xff\xff\x00\xfe\xfe\xfe\xfe\xfd\xfd\xfd\xfd\x12\x34\x56\x78'

# number of query attempts made after the primary attempt failed, each preceded by a warm-up ping
FALLBACK_ATTEMPTS = 2


class QueryNetworkError(Exception):
    """
    Exception thrown when the socket connection fails.
    """
    pass


class QueryFormatError(Exception):
    """
    Exception thrown when the data returned from the server is malformed.
    """
    def __init__(self, raw_data=None):
        if raw_data:
            msg = f"Error parsing data: '{raw_data}'.  Format has likely changed."
        else:
            msg = "Error parsing data from the target server.  Format has likely changed."

        super(QueryFormatError, self).__init__(msg)


class QueryServerData:
    """
    An object encapsulating the data retrieved from a target Minecraft: Bedrock
    edition server using the Query protocol. Note that not all servers provide
    complete or accurate information, so any field could be empty.
    """
    def __init__(self):
        self.motd = None
        self.hostname = None

        self.game_type = None
        self.game_id = None
        self.version = None
        self.server_engine = None

        self.plugins = []
        self.map = None

        self.num_players = -1
        self.max_players = -1
        self.whitelist = None

        self.host_ip = None
        self.host_port = None
        self.players = []

    def __str__(self):
        return "{}({})".format(self.__class__.__name__, ', '.join(f"{k}={repr(v)}" for k, v in self.__dict__.items()))


@contextmanager
def mcquery(host: str, port: int = 19132, timeout: int = 5,
            warmup: bool = False) -> Generator[QueryServerData, None, None]:
    """
    A context manager to make a socket connection to the target host and port,
    then initiates the query protocol sequence to request information about the
    server. The socket connection is automatically closed when the context
    manager exits.

    Some servers silently drop the query packets of "cold" clients and only
    start answering after receiving a RakNet unconnected ping. With ``warmup``
    the ping is sent before the query (for servers known to need it), otherwise
    it is only sent when a query attempt failed. Servers that answer normally
    are not affected by the fallback.
    """
    soc = None

    try:
        logger.debug(f"Connecting to {host}:{port}...")
        soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        soc.settimeout(timeout)
        soc.connect((host, port))

        # Magic + packetType + sessionId
        session_id = randint(1, 9999999)

        if warmup:
            logger.debug("Warm-up ping requested, pinging before querying...")
            _unconnected_ping(soc, timeout)

        data = None
        try:
            # primary attempt: a plain query, same as always
            data = _query_attempt(soc, session_id)
        except (socket.error, QueryFormatError):
            logger.debug("Primary query attempt failed, falling back to warm-up pings...")

            for _ in range(FALLBACK_ATTEMPTS):
                _unconnected_ping(soc, timeout)
                try:
                    data = _query_attempt(soc, session_id)
                    break
                except (socket.error, QueryFormatError):
                    continue

            if data is None:
                raise

        yield data

    except socket.error as msg:
        raise QueryNetworkError(f"Failed to query: '{msg}'")
    finally:
        if soc is not None:
            logger.debug("Closing connection...")
            soc.close()


def _unconnected_ping(soc, timeout: int) -> None:
    """
    Send a RakNet unconnected ping and discard the reply (best-effort warm-up).

    This is only used when a plain query attempt failed, so servers that answer
    normally never receive it. Any error here is ignored: the retry that follows
    is what actually decides the outcome.
    """
    try:
        logger.debug("Sending RakNet unconnected ping (warm-up)...")
        soc.settimeout(min(timeout, 1))
        soc.send(b'\x01'
                 + struct.pack('>Q', int(time.time() * 1000))
                 + RAKNET_PING_MAGIC
                 + struct.pack('>Q', randint(0, 0x7FFFFFFFFFFFFFFF)))
        soc.recv(4096)  # unconnected pong, not needed
    except socket.error:
        pass
    finally:
        soc.settimeout(timeout)


def _query_attempt(soc, session_id: int) -> QueryServerData:
    """
    Perform a single query protocol sequence (handshake + statistics request)
    and return the parsed server data.
    """
    # Magic + packetType + sessionId
    handshake = MC_QUERY_MAGIC + MC_QUERY_HANDSHAKE + struct.pack('>l', session_id)

    logger.debug("Sending handshake...")
    soc.send(handshake)
    response = soc.recv(65535)

    if response[:1] != MC_QUERY_HANDSHAKE:
        raise QueryFormatError(response)

    # The challenge token is echoed back with the statistics request. Most
    # Bedrock cores (PMMP and forks) issue it as a decimal number and expect it
    # back as a big-endian int32, while some servers issue raw binary tokens,
    # which are echoed back as-is.
    token = response[5:].rstrip(b'\x00')
    try:
        token = struct.pack('>l', int(token))
    except ValueError:
        pass

    if not token:
        # an empty token means the query protocol is likely disabled
        raise QueryFormatError

    # Magic + packetType + sessionId + token + payload
    logger.debug("Requesting statistics...")
    request_stat = MC_QUERY_MAGIC + MC_QUERY_STATISTICS + struct.pack('>l', session_id) + token + b'\x00\x00\x00\x00'

    soc.send(request_stat)
    buff = soc.recv(65535)[5:]

    logger.debug("Got data from server.")
    logger.debug("Parsing data...")
    return _parse_data(buff)


def _parse_data(raw_data: bytes) -> QueryServerData:
    """
    Internal function for parsing the raw data from the target server into a
    QueryServerData object.
    """
    stats = QueryServerData()

    server_data = raw_data.split(b'\x01')

    if len(server_data) == 1:
        # Some servers only answer with a short (basic) statistics response:
        # motd\0gametype\0map\0numplayers\0maxplayers\0...
        fields = raw_data.split(b'\x00')
        if len(fields) < 5:
            raise QueryFormatError(raw_data)

        stats.motd = stats.hostname = fields[0].decode('utf-8', errors='replace')
        stats.game_type = fields[1].decode('utf-8', errors='replace')
        stats.map = fields[2].decode('utf-8', errors='replace')
        stats.num_players = _to_int(fields[3], -1)
        stats.max_players = _to_int(fields[4], -1)

        match = re.search(rb'(\d{1,3}(?:\.\d{1,3}){3})', raw_data)
        if match:
            stats.host_ip = match.group(1).decode('utf-8', errors='replace')

        return stats

    if len(server_data) != 2:
        raise QueryFormatError(raw_data)

    server_data_1 = server_data[0].split(b'\x00')[2:-2]
    server_data_2 = server_data[1].split(b'\x00')[2:-2]  # player list

    # trimmed server data
    data = {}
    for i in range(0, len(server_data_1) - 1, 2):
        data[server_data_1[i].decode('utf-8', errors='replace')] = server_data_1[i + 1].decode('utf-8', errors='replace')

    stats.hostname = data.get('hostname')
    stats.game_type = data.get('gametype')
    stats.game_id = data.get('game_id')
    stats.version = data.get('version')
    stats.server_engine = data.get('server_engine')

    # plugins
    plugins = []
    for p in data.get('plugins', '').split(';'):
        plugins.append(p)
    stats.plugins = plugins

    stats.map = data.get('map')
    stats.num_players = _to_int(data.get('numplayers'), -1)
    stats.max_players = _to_int(data.get('maxplayers'), -1)
    stats.whitelist = data.get('whitelist')
    stats.host_ip = data.get('hostip')
    stats.host_port = _to_int(data.get('hostport'), -1)

    players = []
    for p in server_data_2:
        players.append(p.decode('utf-8', errors='replace'))
    stats.players = players

    return stats


def _to_int(value, default: int) -> int:
    """
    Internal function reading an integer field that servers sometimes leave empty.
    """
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def main(args=None):
    parser = argparse.ArgumentParser(description="Query tool for Minecraft: Bedrock Edition servers.")

    parser.add_argument("host", type=str, help="The host of the server.")
    parser.add_argument("-p", "--port", type=int, default=19132, help="The port of the server.")
    parser.add_argument("-t", "--timeout", type=int, default=5, help="The time limit of the socket connection.")
    parser.add_argument("-w", "--warmup", action='store_true',
                        help="Ping the server before querying it, for servers that drop the query packets "
                             "of clients they have not seen pinging yet.")
    parser.add_argument("-d", "--debug", action='store_true', help="Enable debug logging.")

    options = parser.parse_args(args)
    if options.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    host = options.host
    port = options.port
    timeout = options.timeout

    try:
        with mcquery(host, port=port, timeout=timeout, warmup=options.warmup) as data:
            def key(k):
                return k.capitalize().replace('_', ' ')

            stdout: str = '\n'.join(f"{key(k)}: {v}" for k, v in data.__dict__.items())
            print(stdout)
    except Exception as e:
        print(f"An error occurred during query: {e}")


if __name__ == "__main__":
    main(sys.argv[1:])