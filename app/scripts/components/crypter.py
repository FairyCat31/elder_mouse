from cryptography.fernet import Fernet
from json import loads, dumps
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.backends import default_backend
from os import urandom
import hashlib


def gen_salt(size: int = 32) -> bytes:
    return urandom(size)


class Crypter:
    """
    Class for easy decrypt and encrypt STR
    """
    def __init__(self, crypt_key: bytes, encoding: str = "utf-8"):
        """
        crypt_key - symmetric key, which using for decrypt and encrypt data
        encoding - encoding for the convertation data from bytes to string
        """
        self.__fernet = Fernet(crypt_key)
        self.encoding = encoding

    def encrypt(self, data: bytes) -> bytes:
        """ Func for encrypt bytes

        Scheme

        Bytes -> Encrypted bytes
        """

        encrypt_data = self.__fernet.encrypt(data)  # encrypt data
        return encrypt_data

    def decrypt(self, line: bytes) -> bytes:
        """ Func for decrypt bytes

        Scheme

        Encrypted bytes -> Bytes
        """

        decrypt_data = self.__fernet.decrypt(line)  # decrypt data
        return decrypt_data

    def str_encrypt(self, line: str) -> bytes:
        """ Func for encrypt bytes

        Scheme

        Str -> Encrypted bytes
        """

        str_as_bytes = str.encode(line, encoding=self.encoding)  # convert data type of str to bytes
        encrypt_data = self.encrypt(str_as_bytes)
        return encrypt_data

    def str_decrypt(self, data: bytes) -> str:
        """ Func for decrypt bytes

        Scheme

        Encrypted bytes -> Str
        """

        decrypt_data = self.decrypt(data)
        bytes_as_str = decrypt_data.decode(encoding=self.encoding)  # convert data type of bytes to str
        return bytes_as_str


class CrypterDict(Crypter):
    def dict_encrypt(self, dict_for_encrypt: dict) -> bytes:
        """ Func for encrypt dict

        Scheme

        Dict -> encrypt bytes

        """
        print(type(dict_for_encrypt))
        dict_as_str = dumps(dict_for_encrypt)  # convert data type of dict to str
        result = super().str_encrypt(dict_as_str)  # convert to bytes + encrypt
        return result

    def dict_decrypt(self, dict_for_decrypt: bytes) -> dict:
        """ Func for encrypt python dict

        Scheme

        Encrypt bytes -> dict

        """
        result_in_str = super().str_decrypt(dict_for_decrypt)  # decrypt + convert to str
        result = loads(result_in_str)  # convert data type of str to dict
        return result


class AsymmetricCrypter:
    def __init__(self, private_key: rsa.RSAPrivateKey | None = None,
                 public_key: bytes | None = None,
                 encoding: str = "utf-8"):
        if public_key is None:
            self.__public_key = public_key
        else:
            self.__public_key = serialization.load_pem_public_key(public_key)

        self.__private_key = private_key

        self.__padding = padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),
                                      algorithm=hashes.SHA256(),
                                      label=None)
        self.encoding = encoding

    @property
    def public_key(self) -> bytes | None:
        return self.__public_key.public_bytes(
                   encoding=serialization.Encoding.PEM,
                   format=serialization.PublicFormat.SubjectPublicKeyInfo
               )

    @public_key.setter
    def public_key(self, value: bytes):
        self.__public_key = serialization.load_pem_public_key(value)

    def generate_keys(self, key_size: int = 1024, hard_generate: bool = False) -> None:
        if not hard_generate:
            if self.__private_key or self.__public_key:
                return

        self.__private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size,
            backend=default_backend()
        )
        self.__public_key = self.__private_key.public_key()

    def encrypt(self, data: bytes) -> bytes:
        encrypted_data = self.__public_key.encrypt(data, self.__padding)
        return encrypted_data

    def decrypt(self, data: bytes) -> bytes:
        decrypted_data = self.__private_key.decrypt(data, self.__padding)
        return decrypted_data

    def str_encrypt(self, line: str) -> bytes:
        bytes_as_str = line.encode(encoding=self.encoding)
        encrypted_data = self.encrypt(bytes_as_str)
        return encrypted_data

    def str_decrypt(self, data: bytes) -> str:
        decrypted_data = self.decrypt(data)
        decrypted_str = decrypted_data.decode(encoding=self.encoding)
        return decrypted_str


class AsymmetricCrypterDict(AsymmetricCrypter):
    def dict_encrypt(self, dict_for_encrypt: dict) -> bytes:
        """ Func for encrypt dict

        Scheme

        Dict -> encrypt bytes

        """
        dict_as_str = dumps(dict_for_encrypt)  # convert data type of dict to str
        result = super().str_encrypt(dict_as_str)  # convert to bytes + encrypt
        return result

    def dict_decrypt(self, dict_for_decrypt: bytes) -> dict:
        """ Func for encrypt python dict

        Scheme

        Encrypt bytes -> dict

        """
        result_in_str = super().str_decrypt(dict_for_decrypt)  # decrypt + convert to str
        result = loads(result_in_str)  # convert data type of str to dict
        return result


class Hasher:
    def __init__(self, hash_name: str, salt: bytes | int = None):
        self.hash_name = hash_name

        # setting salt
        t_salt = type(salt)
        if t_salt is bytes:
            self.salt = salt
        else:
            self.salt = gen_salt(salt if t_salt is int else 32)

    def data_hash(self, data: bytes, iters: int = 100):
        return hashlib.pbkdf2_hmac(self.hash_name, data, self.salt, iters)
