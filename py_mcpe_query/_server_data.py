"""Query an mcpe server easily

setup.py

Copyright (c) 2017 w-gao
"""

"""
______ ___.__.           _____   ____ ______   ____             ________ __   ___________ ___.__.
\____ <   |  |  ______  /     \_/ ___| |____ \_/ __ \   ______  / ____/  |  \_/ __ \_  __ <   |  |
|  |_> >___  | /_____/ |  Y Y  \  \___|  |_> >  ___/  /_____/ < <_|  |  |  /\  ___/|  | \/\___  |
|   __// ____|         |__|_|  /\___  >   __/ \___  >          \__   |____/  \___  >__|   / ____|
|__|   \/                    \/     \/|__|        \/              |__|           \/       \/
"""


class ServerData:

    SUCCESS = False

    # Motd
    HOSTNAME = 'UNKNOWN'

    GAME_TYPE = 'UNKNOWN'
    GAME_ID = 'UNKNOWN'
    VERSION = '-1'
    SERVER_ENGINE = 'UNKNOWN'

    # Plugin listed
    PLUGINS = []

    # Map name
    MAP = ''

    # Current player count
    NUM_PLAYERS = -1

    # Max player count
    MAX_PLAYERS = 1000

    WHITE_LIST = 'UNKNOWN'

    HOST_IP = 'N/a'
    HOST_PORT = -1

    # List of players online
    PLAYERS = []

    def __str__(self):
        return '{} - {}:{}'.format(self.HOSTNAME, self.HOST_IP, self.HOST_PORT)
