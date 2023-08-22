# SQLAlchemy database connection and configuration
import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import event
from sqlalchemy.engine import Engine
import time
import logging

dateFormat = '%m/%d/%Y %H:%M:%S'
fileFormatter = logging.Formatter(fmt='%(asctime)s %(levelname)-2s | %(message)s', datefmt=dateFormat)
fileHandler = logging.FileHandler(os.path.abspath("./contacts.log"))
fileHandler.setFormatter(fileFormatter)
fileHandler.setLevel(logging.INFO)
logger = logging.getLogger(__name__)
logger.addHandler(fileHandler)
logger.setLevel(logging.INFO)

logger.info("")
logger.info("Session Started")


# @event.listens_for(Engine, "before_cursor_execute")
# def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
#     conn.info.setdefault("query_start_time", []).append(time.time())
#     logger.debug("Start Query: %s", statement)
#
#
# @event.listens_for(Engine, "after_cursor_execute")
# def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
#     total = time.time() - conn.info["query_start_time"].pop(-1)
#     logger.debug("Query Complete!")
#     logger.debug("Total Time: %f", total)


# @event.listens_for(Engine, 'close')
# def receiveClose(dbapi_connection, connection_record):
#     cursor = dbapi_connection.cursor()
#     # cursor.execute("PRAGMA analysis_limit=400")
#     # cursor.execute("PRAGMA optimize")


@event.listens_for(Engine, "connect")
def setSQLitePragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode = MEMORY")
    cursor.execute("PRAGMA synchronous = OFF")
    cursor.execute("PRAGMA temp_store = MEMORY")
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


# insert csvs into empty database:
# no pragmas: 92 seconds, 97 seconds, 91 seconds  # fuck
# pragmas: 27 seconds, 26 seconds, 26 seconds

def renewDbSession():
    global dbSession  # man this is bad
    dbSession.expire_all()
    dbSession.close()
    dbSession = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine, ))
    logger.info("Renewed db session")
    print("RENEWED DB SESSION")

SQLALCHEMY_DATABASE_URL = 'sqlite:///contacts.db'

engine = create_engine(SQLALCHEMY_DATABASE_URL,echo="debug")

dbSession = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Base = declarative_base()
Base.query = dbSession.query_property()
