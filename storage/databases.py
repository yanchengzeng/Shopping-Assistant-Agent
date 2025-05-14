import logging
import os
from sqlalchemy import String, create_engine

logging.getLogger('sqlalchemy').setLevel(logging.WARNING)
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
logging.getLogger('sqlalchemy.pool').setLevel(logging.WARNING)

_db_engine = None


def use_sqlite():
    sqlite_db_file_name = "products.db"
    sqlite_db_dir_name = os.path.dirname(os.path.realpath(__file__))
    sqlite_db_file_path = sqlite_db_dir_name + '/../data/' + sqlite_db_file_name
    return create_engine(f'sqlite:///{sqlite_db_file_path}')


def set_db(engine):
    global _db_engine
    _db_engine = engine


def get_db():
    global _db_engine
    if _db_engine is None:
        _db_engine = use_sqlite()
    return _db_engine
