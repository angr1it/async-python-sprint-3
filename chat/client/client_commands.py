from typing import List
from aiohttp import ClientWebSocketResponse
import logging

from ..command_types import CommandType
from ..exceptions import (
    UnsuitableCommand,
    CommandArgError,
    EmptyCommand
)

logger = logging.getLogger()


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
        
        await websocket.send_json({'command': command, 'message': content})


class QuitCommand(Command):
    @classmethod
    async def run(cls, websocket: ClientWebSocketResponse, command: str = None, content: str = None):
        super().run(websocket, command)

        if not command == CommandType.quit:
            raise UnsuitableCommand
        
        await websocket.close()


class JoinRoom(Command):
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
        
        await websocket.send_json({'command': command, 'room': content})


class SetName(Command):
    @classmethod
    async def run(cls, websocket: ClientWebSocketResponse, command: str = None, content: str = None):
        super().run(websocket, command)

        if not command == CommandType.set_name:
            raise UnsuitableCommand
        if not content:
            raise CommandArgError
        if len(content) == 0:
            raise CommandArgError

        await websocket.send_json({'command': command, 'username': content})

class History(Command):
    @classmethod
    async def run(cls, websocket: ClientWebSocketResponse, command: str = None, content: str = None):
        super().run(websocket, command)

        if not command == CommandType.history:
            raise UnsuitableCommand
        
        try:
            n = int(content)
        except:
            logger.info(f"Couldn't parse n as number of messages in /history; set as default value n = 20.")
            n = 20

        await websocket.send_json({'command': command, 'n': n})

class UserList(Command):
    @classmethod
    async def run(cls, websocket: ClientWebSocketResponse, command: str = None, content: str = None):
        super().run(websocket, command)
        
        if not command == CommandType.user_list:
            raise UnsuitableCommand
        
        await websocket.send_json({'command': command, 'room': content})


class Register(Command):
    @classmethod
    async def run(cls, websocket: ClientWebSocketResponse, command: str = None, content: str = None):
        super().run(websocket, command)

        if not command == CommandType.register:
            raise UnsuitableCommand
        
        try:
            username, key = content.split(' ', 1)
        except:
            logger.info(f"/register [username] [key] --required format")
            raise CommandArgError("/register [username] [key] --required format")

        await websocket.send_json({'command': command, 'username': username, 'key': key})

class Login(Command):
    @classmethod
    async def run(cls, websocket: ClientWebSocketResponse, command: str = None, content: str = None):
        super().run(websocket, command)

        if not command == CommandType.login:
            raise UnsuitableCommand
        
        try:
            username, key = content.split(' ', 1)
        except:
            logger.info(f"/login [username] [key] --required format")
            raise CommandArgError("/login [username] [key] --required format")

        await websocket.send_json({'command': command, 'username': username, 'key': key})

class Logout(Command):
    @classmethod
    async def run(cls, websocket: ClientWebSocketResponse, command: str = None, content: str = None):
        super().run(websocket, command)

        if not command == CommandType.logout:
            raise UnsuitableCommand

        await websocket.send_json({'command': command})