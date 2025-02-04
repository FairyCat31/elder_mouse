from utils.ujson import AddressType, JsonManagerWithCrypt
from factory.errors import FactoryStartArgumentError
from sys import argv as sys_argv
from json import loads, dumps
from typing import Any
import bot_manager


__all__ = [
    "Main"
]
"""
0 - all ok
1 - unknown arg format
2 - func arg set earlier than func
3 - args not set
4 - unknown procedure
"""


class ArgParser:
    def __init__(self):
        self.func_count = -1
        self.error_arg = ""
        self.code = 0

    # convert sub argument value to right data type
    @staticmethod
    def __convert_sub_arg(value: str) -> Any:

        if value.isdigit():
            return int(value)
        elif value.replace('.', '', 1).isdigit():
            return float(value)
        elif value[0] == "[" or value[0] == "{":
            return loads(value)
        elif value.lower() in ["true", "yes", "y"]:
            return True
        elif value.lower() in ["false", "no", "n"]:
            return False
        return value

    def parse_args(self, main_obj, procs_obj) -> int:
        # start parsing

        len_args = len(sys_argv)
        # check if set args
        if len_args == 1:
            self.code = 3

        for i in range(1, len_args):
            arg = sys_argv[i]
            # check is correct format
            if arg[0] != "-":
                self.code = 1
                self.error_arg = arg
                break

            if arg[1] == "-":
                if self.func_count == -1:
                    self.error_arg = arg
                    self.code = 2
                    break
                pd_arg = arg.split("=")
                main_obj.func_args[self.func_count][pd_arg[0][2:]] = self.__convert_sub_arg(pd_arg[1])

            else:
                self.func_count += 1
                main_obj.func_args.append({})
                try:
                    main_obj.start_func.append(getattr(procs_obj, arg[1:]))
                except AttributeError:
                    self.error_arg = arg
                    self.code = 4
                    break

        return self.code


class StartProcedures:

    @staticmethod
    def h():
        return StartProcedures.help()

    @staticmethod
    def help():
        print("""
ALL START ARGS""")

    @staticmethod
    def launch_bot(**kwargs):
        bm = bot_manager.BotManager(debug_mode=kwargs["debug_mode"], advanced_logging=kwargs["advanced_logging"])
        bm.init_bot(**kwargs)
        bm.run_bot()

    @staticmethod
    def add_db(db_data: dict):
        jsm = JsonManagerWithCrypt(AddressType.CFILE, ".dbs.crptjson")
        jsm.load_from_file()
        for name, data in db_data.items():
            jsm[name] = data
        jsm.write_in_file()

    @staticmethod
    def show_db(name: str = ""):
        jsm = JsonManagerWithCrypt(AddressType.CFILE, ".dbs.crptjson")
        jsm.load_from_file()
        if name:
            print(dumps(jsm[name], indent=2))
        else:
            print(dumps(jsm.buffer, indent=2))

    @staticmethod
    def del_db(name: str = ""):
        jsm = JsonManagerWithCrypt(AddressType.CFILE, ".dbs.crptjson")
        jsm.load_from_file()
        b = jsm.buffer
        if name:
            del b[name]
        else:
            b = {}
        jsm.buffer = b
        jsm.write_in_file()

    @staticmethod
    def add_serv(db_data: dict):
        jsm = JsonManagerWithCrypt(AddressType.CFILE, ".rcon_servers.crptjson")
        jsm.load_from_file()
        for name, data in db_data.items():
            jsm[name] = data
        jsm.write_in_file()

    @staticmethod
    def show_serv(name: str = ""):
        jsm = JsonManagerWithCrypt(AddressType.CFILE, ".rcon_servers.crptjson")
        jsm.load_from_file()
        if name:
            print(dumps(jsm[name], indent=2))
        else:
            print(dumps(jsm.buffer, indent=2))

    @staticmethod
    def del_serv(name: str = ""):
        jsm = JsonManagerWithCrypt(AddressType.CFILE, ".rcon_servers.crptjson")
        jsm.load_from_file()
        b = jsm.buffer
        if name:
            del b[name]
        else:
            b = {}
        jsm.buffer = b
        jsm.write_in_file()

    @staticmethod
    def test():
        pass


class Main:
    def __init__(self):
        self.start_func = []
        self.func_args = []

    def main(self):
        arg_parser = ArgParser()
        arg_parser.parse_args(self, StartProcedures)
        if arg_parser.code:
            raise FactoryStartArgumentError(arg_parser.code, arg_parser.error_arg)
        for i in range(len(self.func_args)):
            self.start_func[i](**self.func_args[i])


if __name__ == "__main__":
    m = Main()
    m.main()
