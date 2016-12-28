from Query import *
from ServerData import *

# Change the host and port to whatever you want.
host = 'localhost'
port = 19132

query = Query(host, port)
server_data = ServerData(query)

if server_data.SUCCESS:
    print("Host name: " + server_data.HOSTNAME)
    print("Game Type: " + server_data.GAME_TYPE)
    print("Game Id: " + server_data.GAME_ID)
    print("Version: " + server_data.VERSION)
    print("Server Engine: " + server_data.SERVER_ENGINE)
    print("Plugins: ", server_data.PLUGINS)
    print("Map: " + server_data.MAP)
    print("Player count: ", server_data.NUM_PLAYERS, '/', server_data.MAX_PLAYERS)
    print("White list: " + server_data.WHITE_LIST)
    print("Host: " + server_data.HOST_IP, ":", server_data.HOST_PORT)
    print("Players: ", server_data.PLAYERS)
