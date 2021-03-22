import datetime

import sqlalchemy as sa
import sqlalchemy.ext.declarative as dec
import sqlalchemy.orm as orm
from sqlalchemy.orm import Session

SqlAlchemyBase = dec.declarative_base()

__factory = None


def __enter__(self: Session) -> Session:
    return self


def __exit__(self: Session, *args, **kwargs):
    self.close()


Session.__enter__ = __enter__
Session.__exit__ = __exit__


def global_init(db_file):
    global __factory

    if __factory:
        return

    if not db_file or not db_file.strip():
        raise Exception("Необходимо указать файл базы данных.")

    # noinspection PyUnresolvedReferences
    from . import __all_modes

    conn_str = f'sqlite:///{db_file.strip()}?check_same_thread=False'
    print(f"[{datetime.datetime.now()}] [db_session] Подключение к базе данных по адресу {conn_str}")

    engine = sa.create_engine(conn_str, echo=False)
    __factory = orm.sessionmaker(bind=engine)

    SqlAlchemyBase.metadata.create_all(engine)


def create_session() -> Session:
    global __factory
    return __factory()
