import os

from database import SqliteDatabase

database_path = 'test.sqlite'


def test__create_database():
  if os.path.isfile(database_path):
    os.remove(database_path)
  assert not os.path.isfile(database_path)
  database = SqliteDatabase(path=database_path)
  assert os.path.isfile(database_path)
