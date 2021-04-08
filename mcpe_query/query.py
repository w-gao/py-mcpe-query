"""
Copyright (c) 2017 w-gao
"""

import socket
import struct
from random import randint
from typing import Optional


class ServerData:

    def __init__(self):
        self.motd = None
        self.hostname = None

        self.game_type = None
        self.game_id = None
        self.version = None
        self.server_engine = None

        self.plugins = []
        self.map = None,

        self.num_players = -1
        self.max_players = -1
        self.whitelist = None

        self.host_ip = None
        self.host_port = None

        self.players = []

        self.success = False

    def __str__(self):
        return '{} - {}:{}'.format(self.hostname, self.host_ip, self.host_port)


class Query:
    MAGIC = b'\xFE\xFD'
    HANDSHAKE = b'\x09'
    STATISTICS = b'\x00'

    def __init__(self, host: str, port: int, timeout: Optional[int] = 5):
        self.host = host
        self.port = port
        self.timeout = timeout

        self.socket = None

    def query(self) -> ServerData:
        """
        Initiates a query request to the target server. Returns a ServerData
        object containing the data returned from the server.

        :return: data
        """
        stats = ServerData()

        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            self.socket.settimeout(self.timeout)

            self.socket.connect((self.host, self.port))
        except socket.error as msg:
            print("Cannot connect to the server. Error: ", msg)
            return stats

        try:
            # Magic + packetType + sessionId + payload
            handshake = Query.MAGIC + Query.HANDSHAKE + struct.pack('>l', randint(1, 9999999))

            self.socket.send(handshake)
            token = self.socket.recv(65535)[5:-1].decode()

            if token is not None:
                payload = b'\x00\x00\x00\x00'

                request_stat = Query.MAGIC + Query.STATISTICS + struct.pack('>l', randint(1, 9999999)) + struct.pack(
                    '>l', int(token)) + payload

                self.socket.send(request_stat)
                buff = str(self.socket.recv(65535)[5:])

                if buff is not None:
                    return self._parse_data(buff)

        # The server is offline or it did not enable query
        except socket.error as msg:
            print('Failed to query. Error message: ', msg)

        self.socket.close()
        return stats

    @staticmethod
    def _parse_data(raw_data: str) -> ServerData:
        stats = ServerData()

        server_data = raw_data.split(r'\x01')
        assert len(server_data) == 2, f'Error parsing data: "{raw_data}".  Format has likely changed.'

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

        stats.success = True
        return stats
