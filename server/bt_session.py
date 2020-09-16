import threading


class BluetoothSession(threading.Thread):
  def __init__(self, client_sock, client_info):
    super().__init__()
    self.client_sock = client_sock
    self.client_info = client_info

  def run(self) -> None:
    # TODO: read ProtoBuf messages from the socket, handle them, and send responses
    pass
