import sqlite3
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker
from app.scripts.utils.ujson import JsonManagerWithCrypt, AddressType
from sqlalchemy import MetaData
from app.scripts.factory.errors import DatabaseConnectionDataError, DatabaseNameError


class DBType:
    """

    """
    ONLINE_FORMAT = "://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    MariaDB = "mariadb+pymysql" + ONLINE_FORMAT
    MySQL = "mysql+pymysql" + ONLINE_FORMAT
    SQLite3 = "app/data/local_dbs/{db_name}.db"


class DBManager:
    """
    Basic manager for raw interact with db

    Without models and tables shapes
    """
    def __init__(self, database_name: str, db_type: str, echo: bool = False):
        self._db_name = database_name
        # load crypt json which content data for connect to database
        self._json_manager = JsonManagerWithCrypt(AddressType.CFILE, ".dbs.crptjson")
        self._json_manager.load_from_file()
        # get data for connect to database by name which set in param database_name
        # structure of dict {
        # "DB_HOST": STR
        # "DB_PORT": INT
        # "DB_USER": STR
        # "DB_PASS": STR
        # "DB_NAME": STR

        data_for_conn: dict = self._json_manager.buffer.get(database_name)
        if data_for_conn is None:
            raise DatabaseNameError(database_name)
        else:
            for par in ["DB_HOST", "DB_PORT", "DB_USER", "DB_PASS", "DB_NAME"]:
                if data_for_conn.get(par) is None:
                    raise DatabaseConnectionDataError(database_name, par)
        data_for_conn["CONN_URL"] = db_type
        conn_url = self.get_url_by_dict(data_for_conn)
        print(conn_url)
        self.Engine = create_engine(url=conn_url, echo=echo, pool_size=5, max_overflow=10,)
        self.Session = sessionmaker(self.Engine)
        self.metadata_obj = MetaData()

    @staticmethod
    def get_url_by_dict(data_for_conn: dict) -> str:
        conn_address = data_for_conn["CONN_URL"].format(**data_for_conn)
        return conn_address

    @staticmethod
    def db_connect(func):
        """
        Decorator for func, which work with db
        """
        def wrapper(self, *args, **kwargs):
            with self.Engine.connect() as conn:
                res = func(self, conn, *args, **kwargs)
                return res
        return wrapper

    @staticmethod
    def db_session(func):
        def wrapper(self, *args, **kwargs):
            with self.Session() as session:
                res = func(self, session, *args, **kwargs)
                return res
        return wrapper

    # @db_connect
    # def create_tables(self, conn: Connection):
    #     self.metadata_obj.create_all(conn)
    #     conn.commit()
    #
    # @db_connect
    # def drop_tables(self, conn: Connection):
    #     self.metadata_obj.drop_all(conn)
    #     conn.commit()


class LiteDBManager:
    def __init__(self, db_path: str):
        self._db_path = db_path

    @staticmethod
    def db_connect(func):
        def wrapper(self, *args, **kwargs):
            with sqlite3.connect(self._db_path) as conn:
                res = func(self, conn, *args, **kwargs)
                return res
        return wrapper
