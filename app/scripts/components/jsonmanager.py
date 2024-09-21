from json import dump, load, dumps
from typing import Any, List
from json5 import dump as dump5
from json5 import load as load5
from re import search as shape_search
from os.path import exists
from app.scripts.components.crypter import CrypterDict
from dotenv import dotenv_values

PATH_CONFIG_JSON = "app/data/json/json_conf.json"


class AddressType:
    # default path > Young-bot-me/app/data/json
    FILE = "path_to_json_files"
    # default path > Young-bot-me/app/data/json/.crptjson
    CFILE = "path_to_crptjson_files"
    # default path > Where u start bot
    PATH = ""


class JsonManager:
    def __init__(self, address_type: str, address: str, smart_create: bool = True):
        """
        Manager for working json files
        """
        # load config for JsonManager in file json_conf.json
        with open(PATH_CONFIG_JSON, "r") as f:
            self.json_config = load(f)

        # set path and name file
        if address_type:
            self._name = address
            self._path = self.json_config[address_type] + self._name
        else:
            self._path = address
            self._name = self._path.split("/")[-1]
        # create dict which will content all data from file.json
        self._buffer = {}
        if not smart_create:
            return
        if exists(self._path):
            return
        self.write_in_file()

    # methods for buffer

    def __str__(self):
        return dumps(self._buffer)

    def __path_items(self, line: str) -> List[str]:
        res_parse = shape_search("<&(.+?)>", line)
        if res_parse:
            separator = res_parse.group(1)
        else:
            separator = self.json_config["def_separator"]
        path_items = line.split(separator)
        return path_items

    def __getitem__(self, item) -> Any:
        # create vars
        item = str(item)
        object_output = self._buffer.copy()
        # get separator for pars items and path
        path_items = self.__path_items(item)
        # getting need element
        for path_item in path_items:
            object_output = object_output.get(path_item)

        return object_output

    def __setitem__(self, key, value) -> None:
        # create vars
        key = str(key)
        path_items = self.__path_items(key)
        len_items = len(path_items) - 1
        buffer = self._buffer
        # getting needed sector of dict
        for i, k in enumerate(path_items):
            if i == len_items:
                buffer[k] = value
                break
            # create empty dict if address is empty
            buffer.setdefault(k, {})

            buffer = buffer[k]

    def keys(self):
        return self._buffer.keys()

    def items(self):
        return self._buffer.items()

    def values(self):
        return self._buffer.values()

    # manager methods

    # write all data from file to buffer
    def load_from_file(self) -> None:
        with open(self._path, "r", encoding=self.json_config["encoding"]) as f:
            self._buffer = load(f)

    # write all data from buffer to file
    def write_in_file(self) -> None:
        with open(self._path, "w", encoding=self.json_config["encoding"]) as f:
            dump(self._buffer, f, indent=self.json_config["indent"])

    # get all content from buffer
    def get_buffer(self) -> dict:
        return self._buffer.copy()

    # set content to buffer
    def set_buffer(self, dictionary: dict) -> None:
        self._buffer = dictionary.copy()


class JsonManagerWithCrypt(JsonManager):
    def __init__(self, address_type: str,
                 address: str,
                 crypt_key: bytes = None):
        """
        Manager for working json files with crypt technologies
        """

        super().__init__(address_type=address_type, address=address, smart_create=False)
        self._crypter = self.__crypter_init(crypt_key)

    def __crypter_init(self, crypt_key: bytes) -> CrypterDict:
        if not crypt_key:
            env_vars = dotenv_values(self.json_config["env_with_crypt_key"])
            str_crypt_key = env_vars["DEFAULT_CRYPT_KEY"]
            crypt_key = str.encode(str_crypt_key, encoding="utf-8")

        crypter = CrypterDict(crypt_key=crypt_key)
        del env_vars, str_crypt_key, crypt_key
        return crypter

    def write_in_file(self) -> None:
        with open(self._path, "wb") as f:
            dict_as_encrypt_bytes = self._crypter.dict_encrypt(self._buffer)
            f.write(dict_as_encrypt_bytes)

    def load_from_file(self) -> None:
        with open(self._path, "rb") as f:
            encrypt_dict_as_bytes = f.read()
            self._buffer = self._crypter.dict_decrypt(encrypt_dict_as_bytes)


class JsonManager5(JsonManager):
    def load_from_file(self) -> None:
        with open(self._path, "r", encoding=self.json_config["encoding"]) as f:
            self._buffer = load5(f)

    # write all data from buffer to file
    def write_in_file(self) -> None:
        with open(self._path, "w", encoding=self.json_config["encoding"]) as f:
            dump5(self._buffer, f, indent=self.json_config["indent"])
