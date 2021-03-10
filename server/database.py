import logging
import os
import sqlite3
from typing import BinaryIO


class SqliteDatabase:
  def __init__(self, path: str = "test.sqlite"):
    self.logger = logging.getLogger(self.__class__.__name__)
    self.path = path
    if not os.path.isfile(self.path):
      conn = self._get_connection()
      conn.execute('''CREATE TABLE capture (time TIMESTAMP, image BLOB)''')
      conn.close()

  def _get_connection(self):
    return sqlite3.connect(self.path, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)

  def store_capture(self, image: BinaryIO, timestamp: float):
    conn = self._get_connection()
    conn.execute('''INSERT INTO capture VALUES(?, ?)''', (timestamp, image.read()))
    conn.close()
