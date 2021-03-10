#!/usr/bin/env python3

import bluetooth
from database import SqliteDatabase
import threads
from image_camera import ImageCamera
from msg_handler import MessageHandler
# from rasp_pi_camera import RaspPiCamera
import sys
import logging

logging.basicConfig(format='%(asctime)s %(levelname)s %(threadName)s %(name)s %(message)s', level=logging.INFO)


def main(args):
  main_server = MainServer()
  started = main_server.start()
  if started:
    main_server.listen()
  else:
    logging.error("Failed to start server, terminating...")
    exit(-1)


class MainServer:
  BT_UUID = '12007a4e-7d4c-46f2-b76f-fc26b1181d05'

  def __init__(self):
    self.logger = logging.getLogger(self.__class__.__name__)
    # TODO: initialise database?
    self.camera_thread = None
    self.database_thread = None
    self.bt_server_sock = None
    self.bt_sessions = []
    # TODO: load config

  def start(self):
    self.logger.info("Starting servers")
    started_database = self.start_database_thread()
    started_camera = False
    started_bluetooth = False
    if started_database:
      started_camera = self.start_camera_thread()
    if started_database and started_camera:
      started_bluetooth = self.start_bluetooth_server()
    return started_database and started_camera and started_bluetooth

  def start_database_thread(self):
    self.logger.info("Starting camera thread")
    self.database_thread = threads.Database(SqliteDatabase())
    self.database_thread.start()
    return True

  def start_camera_thread(self):
    self.logger.info("Starting camera thread")
    self.camera_thread = threads.Camera(ImageCamera(), self.database_thread)
    self.camera_thread.start()
    return True

  def start_bluetooth_server(self):
    self.logger.info("Starting bluetooth connection listener")
    self.bt_server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    try:
      self.bt_server_sock.bind(("", bluetooth.PORT_ANY))
    except (bluetooth.BluetoothError, OSError) as error:
      self.logger.error("Could not bind bluetooth socket", exc_info=error)
      return False
    try:
      self.bt_server_sock.listen(1)
    except (bluetooth.BluetoothError, OSError) as error:
      self.logger.error("Could not listen on the bluetooth socket", exc_info=error)
      return False
    try:
      bluetooth.advertise_service(self.bt_server_sock, "RPiBtCamera", MainServer.BT_UUID,
                                  service_classes=[MainServer.BT_UUID, bluetooth.SERIAL_PORT_CLASS],
                                  profiles=[bluetooth.SERIAL_PORT_PROFILE])
    except (bluetooth.BluetoothError, OSError) as error:
      self.logger.error("Could not advertise bluetooth service", exc_info=error)
      return False
    return True

  def listen(self):
    while True:
      try:
        # accept blocks until a connection is established
        client_sock, client_addr = self.bt_server_sock.accept()
        logging.info("Accepted session from %s" % client_addr)
        session = threads.Bluetooth(MessageHandler(), self.camera_thread, self.database_thread, client_sock,
                                    client_addr)
        self.bt_sessions.append(session)
        session.start()
      except (bluetooth.BluetoothError, OSError) as error:
        self.logger.error("Failed to accept or start a session", exc_info=error)


if __name__ == "__main__":
  main(sys.argv)
