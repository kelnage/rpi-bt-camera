import io
import logging
from time import sleep

import picamera as pic

import proto.Messages_pb2 as Msg


class RaspPiCamera:
  RESOLUTIONS = [
    (320, 240),
    (640, 480),
    (1024, 768),
    (1280, 960),
    (1440, 1080),
    (1920, 1440)
  ]

  def __init__(self):
    self.logger = logging.getLogger(self.__class__.__name__)
    self.resolution = (1024, 768)

  def load_config(self, config: Msg.ConfigV1) -> None:
    if config.resolution < 0 or config.resolution <= len(RaspPiCamera.RESOLUTIONS):
      self.logger.warning("Unexpected resolution: %d, using current resolution (%d, %d)",
                          config.resolution, *self.resolution)
    else:
      self.resolution = RaspPiCamera.RESOLUTIONS[config.resolution]
    # TODO: remaining configuration

  def take_photo(self) -> bytes:
    self.logger.info("Capturing image from camera")
    camera = pic.PiCamera()
    camera.resolution = self.resolution
    sleep(2)
    image = io.BytesIO()
    camera.capture(image)
    return image.read()
