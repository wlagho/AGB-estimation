import uuid
import psycopg2
from psycopg2.extras import register_uuid
from psycopg2.extras import RealDictCursor
from flask import current_app
from contextlib import contextmanager

@contextmanager
def get_db_connection():
    conn = psycopg2.connect(current_app.config['DATABASE_URL'])
    try:
        # Register UUID adapter
        register_uuid()
        
        # Set up UUID handling
        def adapt_uuid(uuid_obj):
            return str(uuid_obj)
        
        # Register adapter for UUID type
        psycopg2.extensions.register_adapter(uuid.UUID, adapt_uuid)
        
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def execute_query(query, params=None, fetch_one=False, fetch_all=False):
    # print(f" DATABASE: Executing query: {query}")
    # print(f" DATABASE: Params: {params}")
    
    # Process parameters to handle UUIDs
    processed_params = []
    if params:
        for param in params:
            if isinstance(param, uuid.UUID):
                processed_params.append(str(param))
            else:
                processed_params.append(param)
        params = tuple(processed_params)
    
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            try:
                cursor.execute(query, params or ())
                
                if fetch_one:
                    result = cursor.fetchone()
                    # print(f" DATABASE: Fetch one result: {result}")
                    return result
                elif fetch_all:
                    result = cursor.fetchall()
                    # print(f" DATABASE: Fetch all results: {len(result)} rows")
                    return result
                
                print(f" DATABASE: Row count: {cursor.rowcount}")
                return cursor.rowcount
                
            except Exception as e:
                print(f" DATABASE ERROR: {e}")
                print(f" Query: {query}")
                print(f" Params: {params}")
                raise e