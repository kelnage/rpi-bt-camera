from image_camera import ImageCamera
from proto.Messages_pb2 import ConfigV1

test_image_path = 'test/data/rpi-logo.jpg'


def test_take_photo():
  camera = ImageCamera()
  image = camera.take_photo()
  with open(test_image_path, 'rb') as original:
    assert image is not None
    assert original.read() == image.read()
  image.close()


def test_load_config():
  new_test_image_path = 'test/data/rpi-logo.png'
  camera = ImageCamera()
  assert test_image_path == camera.path
  config = ConfigV1()
  config.path = new_test_image_path
  camera.load_config(config)
  assert new_test_image_path == camera.path
