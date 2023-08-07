import logging
import os

from chat.manage_files import send_file
from chat.command_types import CommandType, DOC
from chat.exceptions import UnsuitableCommand, CommandArgError, EmptyCommand
from chat.utils.my_response import WSResponse
from chat.client.command_models import (
    SendModel,
    HistoryModel,
    CreateRoomModel,
    JoinRoomModel,
    AddUserModel,
    RemoveUserModel,
    LeaveRoomModel,
    RegisterModel,
    LoginModel,
    LogoutModel,
    DeleteRoomModel,
    OpenDialogueModel,
    DeleteDialogueModel,
    PublishFileModel,
    LoadFileModel,
)
from chat.client.console import console_output


logger = logging.getLogger()


SEND_PARSE_ERR = "/send <room_name> <message>"
SEND_PRIVATE_PARSE_ERR = "/send_private <to_username> <message>"
HISTORY_PARSE_ERR = "/history [n] [room_name] "
CREATE_ROOM_PARSE_ERR = "/create_room <room_name> <room_type>"
ADD_USER_PARSE_ERR = "/add_user <room_name> <user_name>"
REMOVE_USER_PARSE_ERR = "/remove_user <room_name> <remove_user>"
LEAVE_ROOM_PARSE_ERR = "/leave_room <room_name>"
REGISTER_PARSE_ERR = "/register <username> <password>"
LOGIN_PARSE_ERR = "/login <username> <key>"
PUBLISH_FILE_PARSE_ERR = "/publish_file <path> [user1] [user2]...[usern]"


class Command:
    @classmethod
    def run(cls, ws: WSResponse, command: str, content: str = None):
        if not ws:
            raise RuntimeError("websocket is none!")
        if command is None:
            raise EmptyCommand(f"{cls.__name__}: command is None!")
        if len(command) == 0:
            raise EmptyCommand(f"{cls.__name__}: command is empty!")


class HelpCommand(Command):
    @classmethod
    async def run(cls, ws: WSResponse, command: str, content: str = None):
        super().run(ws, command)

        if not command == CommandType.help:
            raise UnsuitableCommand

        await console_output(DOC)


class SendCommand(Command):
    @classmethod
    async def run(cls, ws: WSResponse, command: str, content: str = None):
        super().run(ws, command)

        if not command == CommandType.send:
            raise UnsuitableCommand

        if not content:
            raise CommandArgError("SendCommand: content is None!")
        if len(content) == 0:
            raise CommandArgError("SendCommand: content is empty!")

        try:
            room, message = content.split(" ", 1)
        except ValueError:
            logger.info(SEND_PARSE_ERR)
            return

        model = SendModel(room=room, message=message)

        await ws.send_json(model.model_dump())


class SendPrivateCommand(Command):
    @classmethod
    async def run(cls, ws: WSResponse, command: str, content: str = None):
        super().run(ws, command)

        if not command == CommandType.send_private:
            raise UnsuitableCommand

        if not content:
            raise CommandArgError("SendCommand: content is None!")
        if len(content) == 0:
            raise CommandArgError("SendCommand: content is empty!")

        try:
            to_user, message = content.split(" ", 1)
        except ValueError:
            logger.info(SEND_PARSE_ERR)
            return

        model = SendModel(to_user=to_user, message=message, private=True)

        await ws.send_json(model.model_dump())


class HistoryCommand(Command):
    @classmethod
    async def run(cls, ws: WSResponse, command: str, content: str = None):
        super().run(ws, command)

        if not command == CommandType.history:
            raise UnsuitableCommand

        notification_count = 20
        room = ""
        if not content:
            content = ""

        try:
            n_str, room = content.split(" ", 1)
            notification_count = int(n_str)
        except ValueError:
            try:
                notification_count = int(content)
            except ValueError:
                room = content.replace(" ", "")

        model = HistoryModel(room=room, notification_count=notification_count)

        await ws.send_json(model.model_dump())


class CreateRoomCommand(Command):
    @classmethod
    async def run(cls, ws: WSResponse, command: str, content: str = None):
        super().run(ws, command)

        if not command == CommandType.create_room:
            raise UnsuitableCommand

        try:
            room_name, room_type = content.split(" ", 1)

        except ValueError:
            logger.info(HISTORY_PARSE_ERR)
            return

        model = CreateRoomModel(room_name=room_name, room_type=room_type)

        await ws.send_json(model.model_dump())


class JoinRoomCommand(Command):
    @classmethod
    async def run(cls, ws: WSResponse, command: str, content: str = None):
        super().run(ws, command)

        if not command == CommandType.join_room:
            raise UnsuitableCommand

        model = JoinRoomModel(room_name=content)

        await ws.send_json(model.model_dump())


class AddUserCommand(Command):
    @classmethod
    async def run(cls, ws: WSResponse, command: str, content: str = None):
        super().run(ws, command)

        if not command == CommandType.add_user:
            raise UnsuitableCommand

        try:
            room_name, new_user = content.split(" ", 1)
        except ValueError:
            logger.info(ADD_USER_PARSE_ERR)
            return

        model = AddUserModel(room_name=room_name, new_user=new_user)

        await ws.send_json(model.model_dump())


class RemoveUserCommand(Command):
    @classmethod
    async def run(cls, ws: WSResponse, command: str, content: str = None):
        super().run(ws, command)

        if not command == CommandType.remove_user:
            raise UnsuitableCommand

        try:
            room_name, remove_user = content.split(" ", 1)
        except ValueError:
            logger.info(REMOVE_USER_PARSE_ERR)
            return

        model = RemoveUserModel(room_name=room_name, remove_user=remove_user)

        await ws.send_json(model.model_dump())


class LeaveRoomCommand(Command):
    @classmethod
    async def run(cls, ws: WSResponse, command: str, content: str = None):
        super().run(ws, command)

        if not command == CommandType.leave_room:
            raise UnsuitableCommand

        try:
            room_name = content
        except ValueError:
            logger.info(REMOVE_USER_PARSE_ERR)
            return

        model = LeaveRoomModel(room_name=room_name)

        await ws.send_json(model.model_dump())


class RegisterCommand(Command):
    @classmethod
    async def run(cls, ws: WSResponse, command: str, content: str = None):
        super().run(ws, command)

        if not command == CommandType.register:
            raise UnsuitableCommand

        try:
            username, password = content.split(" ", 1)
        except ValueError:
            logger.info(REGISTER_PARSE_ERR)
            return

        model = RegisterModel(username=username, password=password)

        await ws.send_json(model.model_dump())


class LoginCommand(Command):
    @classmethod
    async def run(cls, ws: WSResponse, command: str, content: str = None):
        super().run(ws, command)

        if not command == CommandType.login:
            raise UnsuitableCommand

        try:
            username, password = content.split(" ", 1)
        except ValueError:
            logger.info(LOGIN_PARSE_ERR)
            return

        model = LoginModel(username=username, password=password)

        await ws.send_json(model.model_dump())


class LogoutCommand(Command):
    @classmethod
    async def run(cls, ws: WSResponse, command: str, content: str = None):
        super().run(ws, command)

        if not command == CommandType.logout:
            raise UnsuitableCommand

        await ws.send_json(LogoutModel().model_dump())


class QuitCommand(Command):
    @classmethod
    async def run(cls, ws: WSResponse, command: str, content: str = None):
        super().run(ws, command)

        if not command == CommandType.quit:
            raise UnsuitableCommand

        raise KeyboardInterrupt


class DeleteRoomCommand(Command):
    @classmethod
    async def run(cls, ws: WSResponse, command: str, content: str = None):
        super().run(ws, command)

        if not command == CommandType.delete_room:
            raise UnsuitableCommand

        model = DeleteRoomModel(room_name=content)

        await ws.send_json(model.model_dump())


class OpenDialogueCommand(Command):
    @classmethod
    async def run(cls, ws: WSResponse, command: str, content: str = None):
        super().run(ws, command)

        if not command == CommandType.open_dialogue:
            raise UnsuitableCommand

        model = OpenDialogueModel(with_user=content)

        await ws.send_json(model.model_dump())


class DeleteDialogueCommand(Command):
    @classmethod
    async def run(cls, ws: WSResponse, command: str, content: str = None):
        super().run(ws, command)

        if not command == CommandType.delete_dialogue:
            raise UnsuitableCommand

        model = DeleteDialogueModel(with_user=content)

        await ws.send_json(model.model_dump())


class PublishFileCommand(Command):
    @classmethod
    async def run(cls, ws: WSResponse, command: str, content: str = None):
        super().run(ws, command)

        if not command == CommandType.publish_file:
            raise UnsuitableCommand

        if not os.path.isfile(path=content):
            logger.error("/publish_file: File does not exist!")
            return

        filename = os.path.basename(content)

        model = PublishFileModel(filename=filename)

        await ws.send_json(model.model_dump())

        await send_file(ws=ws, path=content)


class LoadFileCommand(Command):
    @classmethod
    async def run(cls, ws: WSResponse, command: str, content: str = None):
        super().run(ws, command)

        if not command == CommandType.load_file:
            raise UnsuitableCommand

        model = LoadFileModel(key=content)

        await ws.send_json(model.model_dump())
