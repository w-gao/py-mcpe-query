# mcquery

[![PyPI](https://img.shields.io/pypi/v/mcquery.svg)](https://pypi.python.org/pypi/mcquery/)


## Introduction
------------
mcquery (aka py-mcpe-query) is a Python software that uses the query protocol to ping a Minecraft: Bedrock edition 
server for basic information. Note: If you get a timeout error, it might be that the target server do not support the 
query protocol. If that happens, you can use [py-mcpe-stats](https://github.com/w-gao/py-mcpe-stats) where you can 
ping a server without the query protocol.

## Install
-------

#### Install via pip
Run `pip install mcquery` in your terminal, and it will download the latest version of this project.

#### Install from source

Clone this repository and run the following in the root folder of this project:
```
python setup.py build
python setup.py install
```

## Usage
-----

#### Query with CLI

After installation, the `mcquery` command will be available in your Python environment. You can perform a query with 
the following command: `mcquery localhost`.

You can also provide the port with the `-p` option as such `mcquery localhost -p 19133`. For more options, please run 
`mcquery --help`.


#### Use as a module

You can also use the API by writing the following code in your project:

```python
from mcquery import mcquery

host = "localhost"
port = 19132

with mcquery(host, port=port, timeout=10) as data:
    # data is a QueryServerData instance
    print(data)
```

## License
-------

MIT &copy; 2017-2021 w-gao
