import logging
import threads
import proto.Messages_pb2 as Msg


class MessageHandler:
  def __init__(self):
    self.logger = logging.getLogger(self.__class__.__name__)

  def handle_command(self, command: Msg.CommandV1, camera: threads.Camera, database: threads.Database) -> Msg.ResponseV1:
    if command.action == Msg.CommandV1.Action.end_session:
      return None
    else:
      response = Msg.ResponseV1()
      if command.action == Msg.CommandV1.Action.get_config:
        pass
      elif command.action == Msg.CommandV1.Action.set_config:
        pass
      elif command.action == Msg.CommandV1.Action.get_latest_images:
        pass
      elif command.action == Msg.CommandV1.Action.capture_image:
        camera.capture_image()

      return response
