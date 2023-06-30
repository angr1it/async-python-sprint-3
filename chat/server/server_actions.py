from typing import List, Dict, Tuple, Union
from aiohttp import ClientWebSocketResponse
import logging
from datetime import datetime
import dataclasses
from aiohttp import web
from aiohttp.web_request import Request

logger = logging.getLogger()

from ..command_types import CommandType
from .actions import ActionMessages

from ..exceptions import (
    UnsuitableCommand,
    CommandArgError,
    EmptyCommand
)

from .utils import broadcast, get_anonymous_nick
from .message import Message
from .meta import Meta
from .message import MessageStore
from .users import UserStore

class Command:
    @classmethod
    async def run(cls, request: Request, ws_response: web.WebSocketResponse, meta: Meta, command: str = None, message_json: Dict[str, str] = None) -> web.WebSocketResponse:
        pass
        

class JoinRoom(Command):

    @staticmethod
    def __change_room(app: web.Application, new_room: str, old_room: str, user: str) -> Tuple[Dict, bool]:
        """
        Takes a user and changes it's connected room.
        :param app: Application
        :param new_room: New room name
        :param old_room: Old room name
        :return: A tuple that contains the dict to return to the end user, as well as 
        """
        if not isinstance(new_room, str) or not 3 <= len(new_room) <= 20:
            return (
                ActionMessages.join_room(username=user, room=new_room, success=False, message='Room name must be a string and between 3-20 chars.'),
                False
            )
        
        if user in app['websockets'][new_room].keys():
            return (
                ActionMessages.join_room(username=user, room=new_room, success=False, message='Name already in use in this room.'),
                False
            )
        
        app['websockets'][new_room][user] = app['websockets'][old_room].pop(user)
        return (ActionMessages.join_room(username=user, room=new_room, success=True, message=''), True)
    
    @staticmethod
    def __to_logger(room: str, user: str, to_room: str, reason: str):
        logger.info(
                '%s: Unable to change room for %s to %s, reason: %s',
                room,
                user,
                to_room,
                reason
            )
    
    @classmethod
    async def run(cls, request: Request, ws_response: web.WebSocketResponse, meta: Meta, command: str = None, message_json: Dict[str, str] = None):
        
        if not command == CommandType.join_room:
            raise UnsuitableCommand
        
        if not 'room' in message_json.keys():
            await ws_response.send_json(
                ActionMessages.join_room(username=meta.username, room='', success=False, message='Room was not specified.')
            )
            JoinRoom.__to_logger(meta.room, meta.username, '', 'Room was not specified.')
            return meta

        if not meta.loggedin and not message_json.get('room') == 'Global':
            await ws_response.send_json(
                ActionMessages.join_room(username=meta.username, room='', success=False, message='User must be logged-in to leave Global room.')
            )
            JoinRoom.__to_logger(meta.room, meta.username, message_json.get('room'), 'User must be logged-in to leave Global room.')
            return meta
        
        return_body, success = JoinRoom.__change_room(
            app=request.app, new_room=message_json.get('room'), old_room=meta.room, user=meta.username
        )

        if not success:
            JoinRoom.__to_logger(meta.room, meta.username, message_json.get('room'), return_body['message'])
            await ws_response.send_json(return_body)
            return meta
        
        logger.info('%s: User %s joined the room', meta.username, message_json.get('room'))

        await broadcast(
            app=request.app,
            room=meta.room,
            message=ActionMessages.left_room(meta.username, meta.room, False),
        )

        await broadcast(
            app=request.app,
            room=message_json.get('room'),
            message=ActionMessages.join_room(username=meta.username, room=meta.room, success=True, message=''),
            ignore_user=meta.username,
        )
        meta.room = message_json.get('room')

        return meta


class Register(Command):

    async def __register_new(username: str, key: str):

        if UserStore().register(username=username, key=key):
            return ActionMessages.register(username=username, success=True, reason='')
        
        return ActionMessages.register(username=username, success=False, reason='User with this name already exists.')
    
    @classmethod
    async def run(cls, request: Request, ws_response: web.WebSocketResponse, meta: Meta, command: str = None, message_json: Dict[str, str] = None):

        if not command == CommandType.register:
            raise UnsuitableCommand
        
        if meta.loggedin:
            await ws_response.send_json(
                ActionMessages.register(username=meta.username, success=False, reason='You need to be logged out to register.')
            )
            return meta

        try:
            username = message_json.get('username')
            key = message_json.get('key')
        except:
            await ws_response.send_json(
                ActionMessages.register(username=meta.username, success=False, reason='(Username,key) combination required.')
            )
            return meta
        
        return_body = await Register.__register_new(username=username, key=key)

        await ws_response.send_json(return_body)

        return meta


class Login(Command):
    @staticmethod
    def __to_logger(room: str, user: str, reason: str):
        logger.info(
                '%s: Unable to login to %s, reason: %s',
                room,
                user,
                reason
            )

    @classmethod
    async def run(cls, request: Request, ws_response: web.WebSocketResponse, meta: Meta, command: str = None, message_json: Dict[str, str] = None):
        
        if not command == CommandType.login:
            raise UnsuitableCommand

        if meta.loggedin:
            Login.__to_logger(meta.room, meta.username, f'Already logged in under {meta.username}')
            await ws_response.send_json(
                ActionMessages.login(username='', success=False, reason=f'Already logged in under {meta.username}. Try log out first.')
                )
            return meta
        
        try:
            username = message_json.get('username')
            key = message_json.get('key')
        except:
            Login.__to_logger(meta.room, meta.username, f'Both (username,key) expected.')
            await ws_response.send_json(
                ActionMessages.login(username='', success=False, reason='Both (username,key) expected.')
            )
            return meta
        
        if not UserStore().login(username=username, key=key):
            Login.__to_logger(meta.room, meta.username, f'Failed to login under {username}. Incorrect (username,key) combination.')
            await ws_response.send_json(
                    ActionMessages.login(username=username, success=False, reason=f'Incorrect (username,key) combination.')
                )
            return meta
        
        await broadcast(
            app=request.app,
            room=meta.room,
            message=ActionMessages.left_room(meta.username, meta.room, False),
        )

        request.app['websockets'][meta.room].pop(meta.username)

        meta.username = username
        meta.loggedin = True
        request.app['websockets'][meta.room][meta.username] = ws_response

        await ws_response.send_json(
            ActionMessages.login(username=username, success=True, reason='')
        )

        await broadcast(
            app=request.app,
            room=message_json.get('room'),
            message=ActionMessages.join_room(username=meta.username, room=meta.room, success=True, message=''),
            ignore_user=meta.username,
        )

        logger.info('%s: %s logged in.', meta.room, meta.username)
        
        return meta


class Logout(Command):

    @staticmethod
    def __to_logger(room: str, user: str, reason: str):
        logger.info(
                '%s: Unable to logout from user %s, reason: %s',
                room,
                user,
                reason
            )
    

    @classmethod
    async def run(cls, request: Request, ws_response: web.WebSocketResponse, meta: Meta, command: str = None, message_json: Dict[str, str] = None):
        
        if not command == CommandType.logout:
            raise UnsuitableCommand

        if not meta.loggedin:
            Logout.__to_logger(meta.room, meta.username, f'{meta.username} is anonymous.')

            await ws_response.send_json(
                ActionMessages.logout(username=meta.username, success=False, reason=f'{meta.username} is anonymous.')
            )

            return meta
        
        if not meta.room == 'Global':
            meta = await JoinRoom.run(
                request=request,
                ws_response=ws_response,
                meta=meta,
                command=CommandType.join_room,
                message_json={'room': 'Global'},
                )

        await broadcast(
            app=request.app,
            room=meta.room,
            message=ActionMessages.left_room(meta.username, meta.room, False),
        )

        old_user = meta.username
        request.app['websockets'][meta.room].pop(meta.username)

        meta.loggedin = False
        new_user = get_anonymous_nick()
        meta.username = new_user
        request.app['websockets'][meta.room][meta.username] = ws_response

        logger.info('%s logged out. %s connected to room %s', meta.username, new_user, meta.room)

        await broadcast(
            app=request.app,
            room=meta.room,
            message=ActionMessages.join_room(username=meta.username, room=meta.room, success=True, message=''),
            ignore_user=meta.username,
        )

        await ws_response.send_json(
                ActionMessages.logout(username=meta.username, success=True, reason=f'Logged out from {old_user}')
            )
        
        return meta


class History(Command):

    @staticmethod
    async def __get_messages(room: str, n: int = 20):
        """
        Gets last n Messages as list

        :param app: Application. From a request, pass `request.app`
        :param n: max number of messages  to return from `app['websockets']['messages']`
        """
        
        messages = MessageStore().get_n_messages(room=room, n=n)

        if messages:
            if len(messages) > 0:
                content = [dataclasses.asdict(msg) for msg in messages]
                return ActionMessages.history(room, True, n, content), True
        
        return ActionMessages.history(room, False, n, []), False
    
    @classmethod
    async def run(cls, request: Request, ws_response: web.WebSocketResponse, meta: Meta, command: str = None, message_json: Dict[str, str] = None):
        
        if not command == CommandType.history:
            raise UnsuitableCommand
        
        try:
            n = message_json.get('n')
        except:
            n = 20

        return_body, success = await History.__get_messages(room=meta.room, n=n)

        await ws_response.send_json(return_body)

        if not success:
            logger.warning(f'Failed to send history of messages to {meta.username}. No messages yet')
            return meta
        
        logger.warning(f'History send to {meta.username}.')

        return meta


class UserList(Command):
    @classmethod
    async def run(cls, request: Request, ws_response: web.WebSocketResponse, meta: Meta, command: str = None, message_json: Dict[str, str] = None):
        #super().run(ws_response, command)

        if not command == CommandType.user_list:
            raise UnsuitableCommand

        logger.info('%s: %s requested user list', meta.room, meta.username)

        user_list = ActionMessages.user_list(meta.room, list(request.app['websockets'][meta.room].keys()))
        await ws_response.send_json(user_list)

        return meta
    

class Send(Command):

    @classmethod
    async def run(cls, request: Request, ws_response: web.WebSocketResponse, meta: Meta, command: str = None, message_json: Dict[str, str] = None):
        #super().run(ws_response, command)

        if not command == CommandType.send:
            raise UnsuitableCommand

        logger.info('%s: Message: %s', meta.room, message_json.get('message'))
        MessageStore().add(
            room=meta.room,
            message=Message(
                from_user=meta.username,
                to='all',
                private=False,
                room=meta.room,
                message_str=message_json.get('message'),
                datetime=datetime.now()
            )
        )

        await ws_response.send_json( ActionMessages.send_message_accepted(message_json.get('message')) )
        await broadcast(
            app = request.app,
            room = meta.room,
            message = ActionMessages.send_message_room(meta.username, message_json.get('message')),
            ignore_user = meta.username,
        )

        return meta
    

class SendTo(Command):
    pass

class SendFile(Command):
    pass