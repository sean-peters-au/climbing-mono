import threading
import sqlalchemy
import sqlalchemy.orm

class SessionManager:
    _engine = None
    _SessionLocal = None
    _session = threading.local()

    @classmethod
    def init_engine(cls, uri: str):
        cls._engine = sqlalchemy.create_engine(uri, pool_pre_ping=True)
        cls._SessionLocal = sqlalchemy.orm.sessionmaker(autocommit=False, autoflush=False, bind=cls._engine)

    @classmethod
    def get_session(cls) -> sqlalchemy.orm.Session:
        if not hasattr(cls._session, 'session') or cls._session.session is None:
            cls._session.session = cls._SessionLocal()
        return cls._session.session

    @classmethod
    def remove_session(cls):
        if hasattr(cls._session, 'session') and cls._session.session:
            cls._session.session.close()
            cls._session.session = None

    @classmethod
    def get_engine(cls):
        return cls._engine