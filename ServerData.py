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

    def __init__(self, query):
        self.query = query

        self.load_query()

    def __str__(self):
        return '{} - {}:{}'.format(self.HOSTNAME, self.HOST_IP, self.HOST_PORT)

    def load_query(self):
        if self.query is None:
            print('QUERY OBJECT IS NONE!!!')
            return False

        stats = self.query.query()
        if stats is None:
            return False

        server_data = stats.split(r'\x01')
        server_data_1 = server_data[0].split(r'\x00')[2:-2]

        # Player list
        server_data_2 = server_data[1].split(r'\x00')[2:-2]

        # Trimmed Server Data
        data = {}
        for i in range(0, len(server_data_1), 2):
            data[server_data_1[i]] = server_data_1[i + 1]

        self.HOSTNAME = data['hostname']
        self.GAME_TYPE = data['gametype']
        self.GAME_ID = data['game_id']
        self.VERSION = data['version']
        self.SERVER_ENGINE = data['server_engine']

        # Plugins
        plugins = []
        for p in data['plugins'].split(';'):
            plugins.append(p)
        self.PLUGINS = plugins

        self.MAP = data['map']
        self.NUM_PLAYERS = int(data['numplayers'])
        self.MAX_PLAYERS = int(data['maxplayers'])
        self.WHITE_LIST = data['whitelist']
        self.HOST_IP = data['hostip']
        self.HOST_PORT = int(data['hostport'])

        # Players
        players = []
        for p in server_data_2:
            players.append(p)
        self.PLAYERS = players

        self.SUCCESS = True
        return True
