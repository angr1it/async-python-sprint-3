from typing import List
import logging
import os


from ..manage_files import send_file

from ..command_types import CommandType, DOC

from ..exceptions import (
    UnsuitableCommand,
    CommandArgError,
    EmptyCommand
)
from ..utils.my_response import WSResponse
logger = logging.getLogger()

SEND_PARSE_ERR = "/send <room_name> <message> --required format"
SEND_PRIVATE_PARSE_ERR = "/send_private <to_username> <message> --required format"
HISTORY_PARSE_ERR = "/history [n] [room_name]  --required format"
CREATE_ROOM_PARSE_ERR = '/create_room <room_name> <room_type> --required format'
ADD_USER_PARSE_ERR = '/add_user <room_name> <user_name> --required format'
REMOVE_USER_PARSE_ERR = '/remove_user <room_name> <remove_user> --required format'
LEAVE_ROOM_PARSE_ERR = '/leave_room <room_name> --required format'
REGISTER_PARSE_ERR = '/register <username> <password> --required format'
LOGIN_PARSE_ERR = '/login <username> <key> --required format'
PUBLISH_FILE_PARSE_ERR = '/publish_file <path> [user1] [user2]...[usern] --required format'



class Command:
    @classmethod
    def run(cls, websocket: WSResponse, command: str = None, content: str = None):
        if not websocket:
            raise RuntimeError(f'websocket is none!')
        if command == None:
            raise EmptyCommand(f'{cls.__name__}: command is None!')
        if len(command) == 0:
            raise EmptyCommand(f'{cls.__name__}: command is empty!')

class HelpCommand(Command):
    @classmethod
    async def run(cls, websocket: WSResponse, command: str = None, content: str = None):
        super().run(websocket, command)

        if not command == CommandType.help:
            raise UnsuitableCommand
        
        logger.info(DOC)
        
class SendCommand(Command):
    @classmethod
    async def run(cls, websocket: WSResponse, command: str = None, content: str = None):
        super().run(websocket, command)

        if not command == CommandType.send:
            raise UnsuitableCommand
        
        if not content:
            raise CommandArgError('SendCommand: content is None!')
        if len(content) == 0:
            raise CommandArgError('SendCommand: content is empty!')
        
        try:
            room, message  = content.split(' ', 1)
        except ValueError:
            logger.info(SEND_PARSE_ERR)
            return
        
        await websocket.send_json({'command': command, 'message': message, 'room': room, 'private': False, 'to_user': '/all'})

class SendPrivateCommand(Command):
    @classmethod
    async def run(cls, websocket: WSResponse, command: str = None, content: str = None):
        super().run(websocket, command)

        if not command == CommandType.send_private:
            raise UnsuitableCommand
        
        if not content:
            raise CommandArgError('SendCommand: content is None!')
        if len(content) == 0:
            raise CommandArgError('SendCommand: content is empty!')
        
        try:
            to_user, message  = content.split(' ', 1)
        except ValueError:
            logger.info(SEND_PARSE_ERR)
            return
        
        await websocket.send_json({'command': CommandType.send, 'message': message, 'room': '', 'private': True, 'to_user': to_user})
    
class HistoryCommand(Command):
    @classmethod
    async def run(cls, websocket: WSResponse, command: str = None, content: str = None):
        super().run(websocket, command)

        if not command == CommandType.history:
            raise UnsuitableCommand
        
        notification_count = 20
        room = ''
        if not content:
            content = ''
        
        try:
            n_str, room = content.split(' ', 1)
            notification_count = int(n_str)
        except ValueError:
            try:
                notification_count = int(content)
            except ValueError:
                room = content.replace(' ', '')
        
        await websocket.send_json({'command': command, 'room': room, 'notification_count': notification_count})

class CreateRoomCommand(Command):
    @classmethod
    async def run(cls, websocket: WSResponse, command: str = None, content: str = None):
        super().run(websocket, command)

        if not command == CommandType.create_room:
            raise UnsuitableCommand
        
        try:
            room_name, room_type = content.split(' ', 1)
        except ValueError:
            logger.info(HISTORY_PARSE_ERR)
            return

        await websocket.send_json({'command': command, 'room_name': room_name, 'room_type': room_type})

class JoinRoomCommand(Command):
    @classmethod
    async def run(cls, websocket: WSResponse, command: str = None, content: str = None):
        super().run(websocket, command)

        if not command == CommandType.join_room:
            raise UnsuitableCommand
        # if not content:
        #     raise CommandArgError()
        # if len(content) == 0:
        #     raise CommandArgError
        if not content or content == '':
            content = 'Global'
        
        await websocket.send_json({'command': command, 'room_name': content})

class AddUserCommand(Command):
    @classmethod
    async def run(cls, websocket: WSResponse, command: str = None, content: str = None):
        super().run(websocket, command)

        if not command == CommandType.add_user:
            raise UnsuitableCommand
        
        try:
            room_name, new_user = content.split(' ', 1)
        except ValueError:
            logger.info(ADD_USER_PARSE_ERR)
            return

        await websocket.send_json({'command': command, 'room_name': room_name, 'new_user': new_user})

class RemoveUserCommand(Command):
    @classmethod
    async def run(cls, websocket: WSResponse, command: str = None, content: str = None):
        super().run(websocket, command)

        if not command == CommandType.remove_user:
            raise UnsuitableCommand
        
        try:
            room_name, remove_user = content.split(' ', 1)
        except ValueError:
            logger.info(REMOVE_USER_PARSE_ERR)
            return

        await websocket.send_json({'command': command, 'room_name': room_name, 'remove_user': remove_user})
    
class LeaveRoomCommand(Command):
    @classmethod
    async def run(cls, websocket: WSResponse, command: str = None, content: str = None):
        super().run(websocket, command)

        if not command == CommandType.leave_room:
            raise UnsuitableCommand
        
        try:
            room_name = content
        except ValueError:
            logger.info(REMOVE_USER_PARSE_ERR)
            return

        await websocket.send_json({'command': command, 'room_name': room_name})

class RegisterCommand(Command):
    @classmethod
    async def run(cls, websocket: WSResponse, command: str = None, content: str = None):
        super().run(websocket, command)

        if not command == CommandType.register:
            raise UnsuitableCommand
        
        try:
            username, password = content.split(' ', 1)
        except ValueError:
            logger.info(REGISTER_PARSE_ERR)
            return

        await websocket.send_json({'command': command, 'username': username, 'password': password})

class LoginCommand(Command):
    @classmethod
    async def run(cls, websocket: WSResponse, command: str = None, content: str = None):
        super().run(websocket, command)

        if not command == CommandType.login:
            raise UnsuitableCommand
        
        try:
            username, password = content.split(' ', 1)
        except ValueError:
            logger.info(LOGIN_PARSE_ERR)
            return

        await websocket.send_json({'command': command, 'username': username, 'password': password})

class LogoutCommand(Command):
    @classmethod
    async def run(cls, websocket: WSResponse, command: str = None, content: str = None):
        super().run(websocket, command)

        if not command == CommandType.logout:
            raise UnsuitableCommand

        await websocket.send_json({'command': command})

class QuitCommand(Command):
    @classmethod
    async def run(cls, websocket: WSResponse, command: str = None, content: str = None):
        super().run(websocket, command)

        if not command == CommandType.quit:
            raise UnsuitableCommand
        
        await websocket.close()

class DeleteRoomCommand(Command):

    @classmethod
    async def run(cls, websocket: WSResponse, command: str = None, content: str = None):
        super().run(websocket, command)

        if not command == CommandType.delete_room:
            raise UnsuitableCommand
        
        await websocket.send_json({'command': command, 'room_name': content})

class OpenDialogueCommand(Command):
    @classmethod
    async def run(cls, websocket: WSResponse, command: str = None, content: str = None):
        super().run(websocket, command)

        if not command == CommandType.open_dialogue:
            raise UnsuitableCommand
        
        await websocket.send_json({'command': command, 'with_user': content})

class DeleteDialogueCommand(Command):
    @classmethod
    async def run(cls, websocket: WSResponse, command: str = None, content: str = None):
        super().run(websocket, command)

        if not command == CommandType.delete_dialogue:
            raise UnsuitableCommand
        
        await websocket.send_json({'command': command, 'with_user': content})

class PublishFileCommand(Command):

    @classmethod
    async def run(cls, websocket: WSResponse, command: str = None, content: str = None):
        super().run(websocket, command)

        if not command == CommandType.publish_file:
            raise UnsuitableCommand
        
        if not os.path.isfile(path=content):
            logger.error(f'/publish_file: File does not exist!')
            return

        filename = os.path.basename(content)
        
        await websocket.send_json({'command': command, 'filename': filename})
        
        await send_file(ws=websocket, path=content)

class LoadFileCommand(Command):

    @classmethod
    async def run(cls, websocket: WSResponse, command: str = None, content: str = None):
        super().run(websocket, command)

        if not command == CommandType.load_file:
            raise UnsuitableCommand

        await websocket.send_json({'command': command, 'key': content})