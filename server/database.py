import logging
import os
import sqlite3


class SqliteDatabase:
  def __init__(self, path: str = "rpi_camera_server.sqlite"):
    self.logger = logging.getLogger(self.__class__.__name__)
    self.path = path
    if not os.path.isfile(self.path):
      self._create_database()

  def _create_database(self):
    conn = self._get_connection()
    conn.execute('''CREATE TABLE capture (id INTEGER PRIMARY KEY, time TIMESTAMP, image BLOB)''')
    conn.execute('''CREATE TABLE user (id INTEGER PRIMARY KEY, name TEXT)''')
    conn.execute('''CREATE TABLE accesses (user_id INTEGER, capture_id INTEGER, status INTEGER,
                    FOREIGN KEY(user_id) REFERENCES user(id), FOREIGN KEY(capture_id) REFERENCES capture(id))''')
    conn.close()

  def _get_connection(self):
    return sqlite3.connect(self.path, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)

  def store_capture(self, image_data: bytes, timestamp: float):
    conn = self._get_connection()
    conn.execute('''INSERT INTO capture VALUES(?, ?)''', (timestamp, image_data))
    conn.close()
