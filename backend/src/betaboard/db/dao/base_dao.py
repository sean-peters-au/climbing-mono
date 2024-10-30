import functools
import betaboard.db.session_manager as db_session_manager

def with_session(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        session = db_session_manager.SessionManager.get_session()
        try:
            result = func(*args, session=session, **kwargs)
            session.commit()
            return result
        except Exception as e:
            session.rollback()
            raise
        finally:
            db_session_manager.SessionManager.remove_session()
    return wrapper
