from aiomcrcon import Client, RCONConnectionError, IncorrectPasswordError
from app.scripts.utils.ujson import JsonManagerWithCrypt, AddressType
from app.scripts.factory.errors import RCONNameError, RCONConnectionDataError
from typing import List


class RawRconManager:
    """
    Class for working with rcon connections on low lvl
    """
    def __init__(self, host: str, port: int, password: str):
        """
            host - address minecraft server
            port - port for rcon socket (see server.properties)
            password - password for rcon (see server.properties)
        """
        self.__connect_data = {
            "host": host,
            "port": port,
            "password": password
        }
        code, res = self.test_connect()
        self.code, self.res = code, res

    async def test_connect(self) -> (int, str):  # func for test connection
        try:
            async with Client(**self.__connect_data) as _:
                res = "Ok!"
                code = 0
        except RCONConnectionError:
            res = "RCONConnectionError: An error occurred whilst connecting to the server..."
            code = 1
        except IncorrectPasswordError:
            res = "IncorrectPasswordError: The provided password was incorrect..."
            code = 2

        return code, res

    @staticmethod
    def rcon_connect(func):
        async def wrapper(self, *args, **kwargs):
            async with Client(**self.__connect_data) as client:
                func(client, *args, **kwargs)
        return wrapper


class RconManager(RawRconManager):
    """
    Class for working with rcon connection on high lvl
    """
    def __init__(self, name_server: str):
        """
        name_server - server name from file rcon_servers.crptjson
        """
        jsm = JsonManagerWithCrypt(AddressType.CFILE, "rcon_servers.crptjson")
        jsm.load_from_file()
        server_conn_data = jsm.buffer.get(name_server)
        if server_conn_data is None:
            raise RCONNameError(name_server)
        else:
            for key in ["host", "port", "password"]:
                if key not in server_conn_data:
                    raise RCONConnectionDataError(name_server, key)
        super().__init__(**server_conn_data)

    # method for executing commands on the server
    @RawRconManager.rcon_connect
    async def cmd(self, client: Client, commands: List[str], dyn_vars: dict) -> (list, list):
        texts, codes = [], []
        for command in commands:
            command = command.format(**dyn_vars)
            text, code = await client.send_cmd(command)
            texts.append(text)
            codes.append(code)
        return texts, codes
