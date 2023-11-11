import sqlalchemy as sa
from sqlalchemy import create_engine
import sqlalchemy.orm as orm
from sqlalchemy.orm import Session
import sqlalchemy.ext.declarative as dec

SqlAlchemyBase = dec.declarative_base()

__factory = None


def global_init():
    global __factory

    if __factory:
        return


    DB_USER = 'postgres'
    DB_HOST = 'localhost'
    DB_PORT = 5432
    DB_NAME = 'week-messanger'
    DB_PASSWORD = ''
    
    # if not db_file or not db_file.strip():
    #     raise Exception("Необходимо указать файл базы данных.")

    conn_str = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

    engine = create_engine(conn_str, pool_size=50, echo=False)
    engine.url
    __factory = engine
    return engine




def create_session() -> Session:
    engine = global_init()
    Session = orm.sessionmaker(bind=engine)
    session = Session()
    return session
