import logging

import proto.Messages_pb2 as Msg


class ImageCamera:
  def __init__(self):
    self.logger = logging.getLogger(self.__class__.__name__)
    self.path = "test/data/rpi-logo.jpg"

  def load_config(self, config: Msg.ConfigV1) -> None:
    if config.path:
      self.path = config.path

  def take_photo(self) -> bytes:
    self.logger.info("Capturing image %s", self.path)
    try:
      with open(self.path, mode='rb') as image_file:
        image_data = image_file.read()
        return image_data
    except IOError as ioe:
      self.logger.error("Failed to capture image", exc_info=ioe)
