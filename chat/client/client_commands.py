from typing import List
from aiohttp import ClientWebSocketResponse
import logging
from asyncio import StreamReader, StreamWriter
from asyncio import streams
import os

import aiofiles


from ..command_types import CommandType
from ..exceptions import (
    UnsuitableCommand,
    CommandArgError,
    EmptyCommand
)

logger = logging.getLogger()

SEND_PARSE_ERR = "/send [room_name] [to_username] [private := (True/False)] [message] --required format"
HISTORY_PARSE_ERR = "/history [room_name] [n] --required format"
CREATE_ROOM_PARSE_ERR = '/create_room [room_name] [room_type] --required format'
ADD_USER_PARSE_ERR = '/add_user [room_name] [user_name] --required format'
REMOVE_USER_PARSE_ERR = '/remove_user [room_name] [remove_user] --required format'
LEAVE_ROOM_PARSE_ERR = '/leave_room [room_name] --required format'
REGISTER_PARSE_ERR = '/register [username] [password] --required format'
LOGIN_PARSE_ERR = '/login [username] [key] --required format'


class Command:
    @classmethod
    def run(cls, websocket: ClientWebSocketResponse, command: str = None, content: str = None):
        if not websocket:
            raise RuntimeError(f'websocket is none!')
        if command == None:
            raise EmptyCommand(f'{cls.__name__}: command is None!')
        if len(command) == 0:
            raise EmptyCommand(f'{cls.__name__}: command is empty!')

class SendCommand(Command):
    @classmethod
    async def run(cls, websocket: ClientWebSocketResponse, command: str = None, content: str = None):
        super().run(websocket, command)

        if not command == CommandType.send:
            raise UnsuitableCommand
        
        if not content:
            raise CommandArgError('SendCommand: content is None!')
        if len(content) == 0:
            raise CommandArgError('SendCommand: content is empty!')
        
        try:
            room, to_user, private_str, message  = content.split(' ', 3)
            private = private_str == 'True'
        except:
            logger.info(SEND_PARSE_ERR)
            return
        
        await websocket.send_json({'command': command, 'message': message, 'room': room, 'private': private, 'to_user': to_user})

class HistoryCommand(Command):
    @classmethod
    async def run(cls, websocket: ClientWebSocketResponse, command: str = None, content: str = None):
        super().run(websocket, command)

        if not command == CommandType.history:
            raise UnsuitableCommand
        
        try:
            room, n_str = content.split(' ', 1)
            n = int(n_str)
        except ValueError as ex:
            logger.info(HISTORY_PARSE_ERR)
            logger.info(f"Couldn't parse n as number of messages in /history; set as default value n = 20.")
            n = 20
        except:
            logger.info(HISTORY_PARSE_ERR)
            return

        await websocket.send_json({'command': command, 'room': room, 'n': n})

class CreateRoomCommand(Command):
    @classmethod
    async def run(cls, websocket: ClientWebSocketResponse, command: str = None, content: str = None):
        super().run(websocket, command)

        if not command == CommandType.create_room:
            raise UnsuitableCommand
        
        try:
            room_name, room_type = content.split(' ', 1)
        except:
            logger.info(HISTORY_PARSE_ERR)
            return

        await websocket.send_json({'command': command, 'room_name': room_name, 'room_type': room_type})

class JoinRoomCommand(Command):
    @classmethod
    async def run(cls, websocket: ClientWebSocketResponse, command: str = None, content: str = None):
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
    async def run(cls, websocket: ClientWebSocketResponse, command: str = None, content: str = None):
        super().run(websocket, command)

        if not command == CommandType.add_user:
            raise UnsuitableCommand
        
        try:
            room_name, new_user = content.split(' ', 1)
        except:
            logger.info(ADD_USER_PARSE_ERR)
            return

        await websocket.send_json({'command': command, 'room_name': room_name, 'new_user': new_user})

class RemoveUserCommand(Command):
    @classmethod
    async def run(cls, websocket: ClientWebSocketResponse, command: str = None, content: str = None):
        super().run(websocket, command)

        if not command == CommandType.remove_user:
            raise UnsuitableCommand
        
        try:
            room_name, remove_user = content.split(' ', 1)
        except:
            logger.info(REMOVE_USER_PARSE_ERR)
            return

        await websocket.send_json({'command': command, 'room_name': room_name, 'remove_user': remove_user})
    
class LeaveRoomCommand(Command):
    @classmethod
    async def run(cls, websocket: ClientWebSocketResponse, command: str = None, content: str = None):
        super().run(websocket, command)

        if not command == CommandType.leave_room:
            raise UnsuitableCommand
        
        try:
            room_name = content
        except:
            logger.info(REMOVE_USER_PARSE_ERR)
            return

        await websocket.send_json({'command': command, 'room_name': room_name})

class RegisterCommand(Command):
    @classmethod
    async def run(cls, websocket: ClientWebSocketResponse, command: str = None, content: str = None):
        super().run(websocket, command)

        if not command == CommandType.register:
            raise UnsuitableCommand
        
        try:
            username, password = content.split(' ', 1)
        except:
            logger.info(REGISTER_PARSE_ERR)
            return

        await websocket.send_json({'command': command, 'username': username, 'password': password})

class LoginCommand(Command):
    @classmethod
    async def run(cls, websocket: ClientWebSocketResponse, command: str = None, content: str = None):
        super().run(websocket, command)

        if not command == CommandType.login:
            raise UnsuitableCommand
        
        try:
            username, password = content.split(' ', 1)
        except:
            logger.info(LOGIN_PARSE_ERR)
            return

        await websocket.send_json({'command': command, 'username': username, 'password': password})

class LogoutCommand(Command):
    @classmethod
    async def run(cls, websocket: ClientWebSocketResponse, command: str = None, content: str = None):
        super().run(websocket, command)

        if not command == CommandType.logout:
            raise UnsuitableCommand

        await websocket.send_json({'command': command})

class QuitCommand(Command):
    @classmethod
    async def run(cls, websocket: ClientWebSocketResponse, command: str = None, content: str = None):
        super().run(websocket, command)

        if not command == CommandType.quit:
            raise UnsuitableCommand
        
        await websocket.close()

class PublishFile(Command):

    async def __sender(ws: ClientWebSocketResponse, path: str):
        async with aiofiles.open(path, 'rb') as f:
            chunk = await f.read(2 ** 16)
            while isinstance(chunk, bytes):
                await ws.send_bytes(chunk)
                chunk = f.read(2 ** 16)

    @classmethod
    async def run(cls, websocket: ClientWebSocketResponse, command: str = None, content: str = None):
        super().run(websocket, command)

        if not command == CommandType.publish_file:
            raise UnsuitableCommand
        
        try:
            path, options = content.split(' ', 1)
        except:
            raise CommandArgError("/publish_file <path> [user1] [user2]...[usern] --required format")
        
        try:
            usernames = options.split(' ')
        except:
            usernames = []

        if not os.path.isfile(path=path):
            logger.error(f'File does not exist!')

        filename = os.path.basename(path)
        
        await websocket.send_json({'command': command, 'usernames': usernames, 'filename': filename})
        
        await PublishFile.__sender(ws=websocket, path=path)

