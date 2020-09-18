import sqlite3
import contextlib


class DatabaseHandler:
    def __init__(self, database_name):
        self.conn = sqlite3.connect(database_name)

    def sqlquery(self, query, *params, return_type='one'):
        with contextlib.closing(self.conn.cursor()) as c:
            c.execute(query, params)
            if return_type == 'one':
                result = c.fetchone()
            elif return_type == 'all':
                result = c.fetchall()
            elif return_type == 'commit':
                result = None
                self.conn.commit()
            else:
                raise ValueError(f"Unexpected return_type '{return_type}'.")
        return result
