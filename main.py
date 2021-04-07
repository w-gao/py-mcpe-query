"""Query an mcpe server easily

main.py

Copyright (c) 2017 w-gao
"""

from py_mcpe_query.query import Query

# TODO: argparse

# Change the host and port to whatever you want.
host = 'localhost'
port = 19132

q = Query(host, port)
data = q.query()

if data is not None and data.success:
    print("Host name: " + data.hostname)
    print("Game Type: " + data.game_type)
    print("Game Id: " + data.game_id)
    print("Version: " + data.version)
    print("Server Engine: " + data.server_engine)
    print("Plugins: ", data.plugins)
    print("Map: " + data.map)
    print("Player count: ", data.num_players, '/', data.max_players)
    print("White list: " + data.whitelist)
    print("Host: " + data.host_ip, ":", data.host_port)
    print("Players: ", data.players)
