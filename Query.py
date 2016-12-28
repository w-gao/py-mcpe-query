import socket
import struct
from random import randint

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

    def __init__(self, host, port, timeout=5, short_data=False):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.short_data = short_data

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
        stats = None

        # get data from the server
        try:
            # Handshake
            # Magic + packetType + sessionId + payload
            hand_shake = Query.MAGIC + Query.HANDSHAKE + struct.pack("L", randint(1, 9999999))

            self.socket.send(hand_shake)
            token = self.socket.recv(65535)[5:-1].decode()

            if token is not None:
                if self.short_data:
                    payload = b''
                else:
                    payload = b"\x00\x00\x00\x00"

                request_stat = Query.MAGIC + Query.STATISTICS + struct.pack("L", randint(1, 9999999)) + struct.pack(
                    '>l', int(token)) + payload

                self.socket.send(request_stat)
                stats = str(self.socket.recv(65535)[5:])

        # The server is offline or it did not enable query
        except socket.error as msg:
            print('Failed to query. Error message: ', msg)

        # print('closing the socket')
        self.socket.close()
        return stats
