from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from quadra_diag.core.config import get_settings
from quadra_diag.core.logging import get_logger
from quadra_diag.db.models import Base
from quadra_diag.db.migrations import migrate_sqlite_schema

logger = get_logger(__name__)

settings = get_settings()
settings.runtime_dir.mkdir(parents=True, exist_ok=True)
connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, future=True, connect_args=connect_args)
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
    future=True,
)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    if settings.database_url.startswith("sqlite"):
        try:
            migrate_sqlite_schema(engine)
        except Exception as exc:
            logger.warning("Schema migration skipped: %s", exc)


@contextmanager
def session_scope():
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

