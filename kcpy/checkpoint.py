import sqlite3
from typing import Optional

class Checkpoint(object):
    def __init__(self, sqlite_file_path, db_name, consumer_name: str, stream_name: str, shard_id: str) -> None:
        self.sqlite_file_path = sqlite_file_path
        self.db_name = db_name
        self.consumer_name = consumer_name
        self.stream_name = stream_name
        self.shard_id = shard_id

        self.init_db()

    def init_db(self):
        conn = sqlite3.connect(self.sqlite_file_path)
        c = conn.cursor()
        c.execute(f'CREATE TABLE IF NOT EXISTS {self.db_name}'
                  '(consumer_name text, stream_name text, shard_id text, seq_no text)')
        conn.commit()
        conn.close()

    def set(self, seq_no: str) -> None:
        conn = sqlite3.connect(self.sqlite_file_path)
        c = conn.cursor()

        c.execute(f'SELECT seq_no FROM {self.db_name} '
                  f"WHERE consumer_name = '{self.consumer_name}' "
                  f"AND stream_name = '{self.stream_name}'"
                  f"AND shard_id = '{self.shard_id}'")
        row = c.fetchone()

        if not row:
            sql = f'INSERT INTO {self.db_name} (consumer_name, stream_name, shard_id, seq_no) ' + \
                  f"VALUES ('{self.consumer_name}', '{self.stream_name}', '{self.shard_id}', '{seq_no}')"
        else:
            sql = f"UPDATE {self.db_name} SET seq_no = {seq_no} "  \
                  f"WHERE consumer_name = '{self.consumer_name}' " \
                  f"AND stream_name = '{self.stream_name}' "       \
                  f"AND shard_id = '{self.shard_id}'"
        c.execute(sql)
        conn.commit()
        conn.close()

    def get(self) -> Optional[str]:
        conn = sqlite3.connect(self.sqlite_file_path)
        c = conn.cursor()
        c.execute(f'SELECT seq_no FROM {self.db_name} '
                  f"WHERE consumer_name = '{self.consumer_name}' "
                  f"AND stream_name = '{self.stream_name}'"
                  f"AND shard_id = '{self.shard_id}'")
        row = c.fetchone()
        conn.commit()
        conn.close()

        if row:
            return row[0]
        else:
            return None

    def reset(self) -> None:
        conn = sqlite3.connect(self.sqlite_file_path)
        c = conn.cursor()
        c.execute(f'UPDATE {self.db_name} '
                  f'SET seq_no = NULL '
                  f"WHERE consumer_name = '{self.consumer_name}' "
                  f"AND stream_name = '{self.stream_name}' "
                  f"AND shard_id = '{self.shard_id}'")
        conn.commit()
        conn.close()
