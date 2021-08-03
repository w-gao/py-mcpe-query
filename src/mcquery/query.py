#
# Copyright (c) 2017-2021 w-gao
#
import argparse
import logging
import struct
import sys
import socket
from contextlib import contextmanager
from random import randint
from typing import Generator


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.WARNING)


# constants
MC_QUERY_MAGIC = b'\xFE\xFD'
MC_QUERY_HANDSHAKE = b'\x09'
MC_QUERY_STATISTICS = b'\x00'


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
def mcquery(host: str, port: int = 19132, timeout: int = 5) -> Generator[QueryServerData, None, None]:
    """
    A context manager to make a socket connection to the target host and port,
    then initiates the query protocol sequence to request information about the
    server. The socket connection is automatically closed when the context
    manager exits.
    """
    soc = None

    try:
        logger.debug(f"Connecting to {host}:{port}...")
        soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        soc.settimeout(timeout)
        soc.connect((host, port))

        # Magic + packetType + sessionId + payload
        handshake = MC_QUERY_MAGIC + MC_QUERY_HANDSHAKE + struct.pack('>l', randint(1, 9999999))

        logger.debug("Sending handshake...")
        soc.send(handshake)
        token = soc.recv(65535)[5:-1].decode()

        if token is not None:
            payload = b'\x00\x00\x00\x00'

            logger.debug("Requesting statistics...")
            request_stat = MC_QUERY_MAGIC + MC_QUERY_STATISTICS + struct.pack('>l', randint(1, 9999999)) + struct.pack(
                '>l', int(token)) + payload

            soc.send(request_stat)
            buff = str(soc.recv(65535)[5:])

            if buff is not None:
                logger.debug("Got data from server.")
                logger.debug("Parsing data...")
                yield _parse_data(buff)
                return

        raise QueryFormatError

    except socket.error as msg:
        raise QueryNetworkError(f"Failed to query: '{msg}'")
    finally:
        logger.debug("Closing connection...")
        soc.close()


def _parse_data(raw_data: str) -> QueryServerData:
    """
    Internal function for parsing the raw data from the target server into a
    QueryServerData object.
    """
    stats = QueryServerData()

    server_data = raw_data.split(r'\x01')
    if len(server_data) != 2:
        raise QueryFormatError(raw_data)

    server_data_1 = server_data[0].split(r'\x00')[2:-2]
    server_data_2 = server_data[1].split(r'\x00')[2:-2]  # player list

    # trimmed server data
    data = {}
    for i in range(0, len(server_data_1), 2):
        data[server_data_1[i]] = server_data_1[i + 1]

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
    stats.num_players = int(data.get('numplayers', -1))
    stats.max_players = int(data.get('maxplayers', -1))
    stats.whitelist = data.get('whitelist')
    stats.host_ip = data.get('hostip')
    stats.host_port = int(data.get('hostport', -1))

    players = []
    for p in server_data_2:
        players.append(p)
    stats.players = players

    return stats


def main(args=None):
    parser = argparse.ArgumentParser(description="Query tool for Minecraft: Bedrock Edition servers.")

    parser.add_argument("host", type=str, help="The host of the server.")
    parser.add_argument("-p", "--port", type=int, default=19132, help="The port of the server.")
    parser.add_argument("-t", "--timeout", type=int, default=5, help="The time limit of the socket connection.")
    parser.add_argument("-d", "--debug", action='store_true', help="Enable debug logging.")

    options = parser.parse_args(args)
    if options.debug:
        logging.basicConfig(level=logging.DEBUG)

    host = options.host
    port = options.port
    timeout = options.timeout

    try:
        with mcquery(host, port=port, timeout=timeout) as data:
            def key(k):
                return k.capitalize().replace('_', ' ')

            stdout: str = '\n'.join(f"{key(k)}: {v}" for k, v in data.__dict__.items())
            print(stdout)
    except Exception as e:
        print(f"An error occurred during query: {e}")


if __name__ == "__main__":
    main(sys.argv[1:])
