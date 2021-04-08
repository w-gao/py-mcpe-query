# mcpe-query

[![PyPI](https://img.shields.io/pypi/v/py_mcpe_query.svg)](https://pypi.python.org/pypi/py_mcpe_query/)

## Introduction
------------
py-mcpe-query is a Python software that uses the query protocol to ping a Minecraft: Bedrock edition server for basic information.

Note: Some servers don't allow query, check out my other project [py-mcpe-stats](https://github.com/w-gao/py-mcpe-stats) where you can ping a server without the query protocol.

## Install
-------

#### Install via pip
Run `pip install py_mcpe_query` in your terminal, and it will download the latest version of this project.

## Usage
-----
#### Run Directly

Simply execute `python main.py` in the root folder of this project.
It will automatically query the host and port that are set in the `main.py` file.


#### Use as a module

Include the following code in your project:

```python
from mcpe_query import Query

host = 'localhost'
port = 19132

q = Query(host, port)
server_data = q.query()
```

## License
-------

MIT &copy; 2017-2021 w-gao
