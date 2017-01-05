"""Query an mcpe server easily

query.py

Copyright (c) 2017 w-gao
"""

import socket
import struct
from random import randint
from ._server_data import ServerData

"""
______ ___.__.           _____   ____ ______   ____             ________ __   ___________ ___.__.
\____ <   |  |  ______  /     \_/ ___| |____ \_/ __ \   ______  / ____/  |  \_/ __ \_  __ <   |  |
|  |_> >___  | /_____/ |  Y Y  \  \___|  |_> >  ___/  /_____/ < <_|  |  |  /\  ___/|  | \/\___  |
|   __// ____|         |__|_|  /\___  >   __/ \___  >          \__   |____/  \___  >__|   / ____|
|__|   \/                    \/     \/|__|        \/              |__|           \/       \/
"""


class Query:

    MAGIC = b'\xFE\xFD'
    HANDSHAKE = b'\x09'
    STATISTICS = b'\x00'

    def __init__(self, host, port, timeout=5):
        self.host = host
        self.port = port
        self.timeout = timeout

        self.socket = None

    def query(self):

        # init socket
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            self.socket.settimeout(self.timeout)

            self.socket.connect((self.host, self.port))
        except socket.error as msg:
            print("Cannot connect to the server. Error: ", msg)
            return None

        # Returned stats
        stats = ServerData()

        # get data from the server
        try:
            # Handshake
            # Magic + packetType + sessionId + payload
            hand_shake = Query.MAGIC + Query.HANDSHAKE + struct.pack("L", randint(1, 9999999))

            self.socket.send(hand_shake)
            token = self.socket.recv(65535)[5:-1].decode()

            if token is not None:
                payload = b"\x00\x00\x00\x00"

                request_stat = Query.MAGIC + Query.STATISTICS + struct.pack("L", randint(1, 9999999)) + struct.pack(
                    '>l', int(token)) + payload

                self.socket.send(request_stat)
                buff = str(self.socket.recv(65535)[5:])

                if buff is not None:
                    server_data = buff.split(r'\x01')
                    server_data_1 = server_data[0].split(r'\x00')[2:-2]

                    # Player list
                    server_data_2 = server_data[1].split(r'\x00')[2:-2]

                    # Trimmed Server Data
                    data = {}
                    for i in range(0, len(server_data_1), 2):
                        data[server_data_1[i]] = server_data_1[i + 1]

                    stats.HOSTNAME = data['hostname']
                    stats.GAME_TYPE = data['gametype']
                    stats.GAME_ID = data['game_id']
                    stats.VERSION = data['version']
                    stats.SERVER_ENGINE = data['server_engine']

                    # Plugins
                    plugins = []
                    for p in data['plugins'].split(';'):
                        plugins.append(p)
                    stats.PLUGINS = plugins

                    stats.MAP = data['map']
                    stats.NUM_PLAYERS = int(data['numplayers'])
                    stats.MAX_PLAYERS = int(data['maxplayers'])
                    stats.WHITE_LIST = data['whitelist']
                    stats.HOST_IP = data['hostip']
                    stats.HOST_PORT = int(data['hostport'])

                    # Players
                    players = []
                    for p in server_data_2:
                        players.append(p)
                    stats.PLAYERS = players

                    stats.SUCCESS = True

        # The server is offline or it did not enable query
        except socket.error as msg:
            print('Failed to query. Error message: ', msg)

        # print('closing the socket')
        self.socket.close()
        return stats
