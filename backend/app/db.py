from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Iterator

from psycopg import Connection, OperationalError, connect


class DatabaseUnavailableError(RuntimeError):
    pass


def get_database_url() -> str:
    database_url = (os.environ.get("DATABASE_URL") or "").strip()
    if not database_url:
        raise DatabaseUnavailableError("DATABASE_URL is missing")
    return database_url


@contextmanager
def get_connection() -> Iterator[Connection]:
    try:
        conn = connect(get_database_url())
    except (OperationalError, DatabaseUnavailableError) as e:
        raise DatabaseUnavailableError(str(e)) from e

    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

