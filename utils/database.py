import psycopg2
from psycopg2.extras import RealDictCursor
from flask import current_app
from contextlib import contextmanager

@contextmanager
def get_db_connection():
    conn = psycopg2.connect(current_app.config['DATABASE_URL'])
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def execute_query(query, params=None, fetch_one=False, fetch_all=False):
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, params or ())

            if fetch_one:
                return cursor.fetchone()
            elif fetch_all:
                return cursor.fetchall()

            return cursor.rowcount
