import logging
import struct
import threading
import time
from typing import BinaryIO

import google.protobuf.message as pb_msg

import proto.Messages_pb2 as Msg
from msg_handler import MessageHandler


class Database(threading.Thread):
  def __init__(self, database):
    super().__init__()
    # This is a daemon thread - when no other threads are running,
    # this thread will also terminate
    self.daemon = True
    self.database = database

  def get_config(self) -> Msg.ConfigV1:
    return None

  def store_capture(self, image: BinaryIO, timestamp: float) -> bool:
    return False


class Camera(threading.Thread):
  def __init__(self, camera, database: Database, interval=3600):
    super().__init__()
    self.logger = logging.getLogger("%s-%d" % (self.__class__.__name__, time.time()))
    # This is a daemon thread - when no other threads are running,
    # this thread will also terminate
    self.daemon = True
    self.running = False
    self.interval = interval
    self.last_capture = None
    self.camera = camera
    self.database = database

  def run(self) -> None:
    self.running = True
    while self.running:
      self.capture_image()
      time.sleep(self.interval)

  def capture_image(self):
    self.logger.info("Image capture started at %d", time.time())
    image = self.camera.take_photo()
    timestamp = time.time()
    self.last_capture = timestamp
    self.database.store_capture(image, timestamp)
    return image


class Bluetooth(threading.Thread):
  # Pre-compute message length field size
  MSG_LENGTH_FIELD_TYPE = 'I'
  MSG_LENGTH_FORMAT = '>' + MSG_LENGTH_FIELD_TYPE
  MSG_LENGTH_FIELD_SIZE = struct.Struct(MSG_LENGTH_FIELD_TYPE).size

  def __init__(self, handler: MessageHandler, camera: Camera, database: Database, client_sock, client_addr):
    super().__init__()
    self.logger = logging.getLogger("%s-%s-%d" % (self.__class__.__name__, client_addr, time.time()))
    self.handler = handler
    self.camera = camera
    self.database = database
    self.client_sock = client_sock
    self.client_addr = client_addr

  def run(self) -> None:
    active = True
    while active:
      try:
        msg_len_raw = self.client_sock.recv(Bluetooth.MSG_LENGTH_FIELD_SIZE)  # blocks until receiving data
        (msg_len,) = struct.unpack(Bluetooth.MSG_LENGTH_FORMAT, msg_len_raw)

        command = Msg.CommandV1()
        command.ParseFromString(self.__recv(msg_len))

        response = self.handler.handle_command(command, self.camera, self.database)
        if response:
          resp_len = struct.pack(Bluetooth.MSG_LENGTH_FORMAT, response.ByteSize())
          self.client_sock.sendall(resp_len)
          self.client_sock.sendall(response.SerializeToString())
        else:
          active = False
      except pb_msg.DecodeError as error:
        self.logger.error('An error occurred when parsing a received command', exc_info=error)
      except pb_msg.EncodeError as error:
        self.logger.error('An error occurred when creating a response', exc_info=error)
      finally:
        self.client_sock.close()
    else:
      self.client_sock.close()

  def __recv(self, size):
    buffer = b''
    while size > 0:
      chunk = self.client_sock.recv(size)
      if not chunk:
        self.logger.error('Incomplete message received (expected %d bytes, got %d bytes)' %
                          (size + len(buffer), len(buffer)))
      buffer += chunk
      size -= len(chunk)
    return buffer
