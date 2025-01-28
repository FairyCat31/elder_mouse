from aiomcrcon import Client, RCONConnectionError, IncorrectPasswordError
from app.scripts.components.jsonmanager import JsonManagerWithCrypt, AddressType
from typing import List


class RawRconManager:
    def __init__(self, host: str, port: int, password: str):
        self.__connect_data = {
            "host": host,
            "port": port,
            "password": password
        }
        code, res = self.__test_connect(**self.__connect_data)
        self.code, self.res = code, res

    @staticmethod
    async def __test_connect(conn_data: dict) -> (int, str):
        try:
            client = Client(**conn_data)
            await client.connect()
            await client.close()
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
    def __init__(self, conn_name_server: str):
        jsm = JsonManagerWithCrypt(AddressType.CFILE, "rcon_servers.crptjson")
        jsm.load_from_file()
        server_conn_data = jsm[f"servers/{conn_name_server}"]
        super().__init__(**server_conn_data)

    @RawRconManager.rcon_connect
    async def cmd(self, client: Client, commands: List[str], dyn_vars: dict) -> (list, list):
        texts, codes = [], []
        for command in commands:
            command = command.format(**dyn_vars)
            text, code = await client.send_cmd(command)
            texts.append(text)
            codes.append(code)
        return texts, codes
