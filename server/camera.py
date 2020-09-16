# import picamera as pic
import threading
import time


class CameraThread(threading.Thread):
  def __init__(self, interval=3600):
    super().__init__()
    self.interval = interval
    self.last_capture = None
    # This is a daemon thread - when no other threads are running, this thread will also terminate
    self.daemon = True

  def run(self) -> None:
    while True:
      self.last_capture = self.capture_image()
      time.sleep(self.interval)

  def capture_image(self):
    print("Photo taken at", time.time())
    # TODO: use picamera library to take photo
    return time.time()
