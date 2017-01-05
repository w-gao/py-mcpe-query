# py-mcpe-query

![py-mcpe-query](https://github.com/w-gao/py-mcpe-query/blob/master/images/logo.png)

## Introduction
------------
py-mcpe-query is a Python software that uses the query protocol to ping an mcpe server for basic information.

Note: Some servers don't allow query, check out my other project [py-mcpe-stats](https://github.com/w-gao/py-mcpe-stats) where you can ping an server without the query protocol.

## Install
-------
#### Install via pip
Run `pip install py_mcpe_query` in your terminal and it will download the latest version of this project.

## Usage
-----
#### Run Directly

Simply execute `python main.py` in the root folder of this project.
It will automatically query the host and port that are set in the `main.py` file.


#### Use as a module

Include the following code in your project:

```python
from py_mcpe_query import Query

host = 'localhost'
port = 19132

q = Query(host, port)
server_data = q.query()
```

#### License

MIT &copy; 2017 w-gao