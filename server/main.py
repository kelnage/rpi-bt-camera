#!/usr/bin/env python3

import bluetooth
from bt_session import BluetoothSession
from camera import CameraThread
import sys
import logging

logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s %(message)s', level=logging.INFO)


class MainServer:
  BT_UUID = ''

  def __init__(self):
    self.logger = logging.getLogger(self.__class__.__name__)
    # TODO: initialise database?
    self.camera_thread = None
    self.bt_server_sock = None
    self.bt_sessions = []
    # TODO: load config

  def start(self):
    self.logger.info("Starting servers")
    started_camera = self.start_camera_thread()
    started_bluetooth = self.start_bluetooth_server()
    return started_camera and started_bluetooth

  def start_camera_thread(self):
    self.logger.info("Starting camera thread")
    self.camera_thread = CameraThread()
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

  def listen(self):
    while True:
      # accept blocks until a connection is established
      try:
        client_sock, client_info = self.bt_server_sock.accept()
        session = BluetoothSession(client_sock, client_info)
        self.bt_sessions.append(session)
        session.start()
      except (bluetooth.BluetoothError, OSError) as error:
        self.logger.error("Failed to accept connection", exc_info=error)


if __name__ == "__main__":
  main_server = MainServer()
  started = main_server.start()
  if started:
    main_server.listen()
  else:
    logging.error("Failed to start server, terminating...")
    exit(-1)
