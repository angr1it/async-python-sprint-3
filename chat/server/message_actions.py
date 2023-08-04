from typing import Dict
import logging
from aiohttp import web


from ..command_types import CommandType
from ..exceptions import (
    UnsuitableCommand,
    BadRequest,
    NoRegistredUserFound,
)
from .state.meta import Meta
from .state.room import RoomStore
from .state.user import UserStore
from .state.message import NotificationStore, get_message_notification
from .command import Command


logger = logging.getLogger()


class SendAction(Command):

    @classmethod
    async def run(cls, ws_response: web.WebSocketResponse, meta: Meta, command: str = None, message_json: Dict[str, str] = None):
    
        if not command == CommandType.send:
            raise UnsuitableCommand
        
        if message_json == None:
            raise ValueError
        
        try:
            message = message_json['message']
            room_name = message_json['room']
            private = bool(message_json['private'])
            to_user = message_json['to_user']
        except:
            raise BadRequest
        
        await NotificationStore().process(
            ws=ws_response,
            notification=get_message_notification(room_name=room_name, user_name=meta.user_name, success=True, reason='', private=private, to=to_user, message=message)
        )

        return meta

class HistoryAction(Command):
    @classmethod
    async def run(cls, ws_response: web.WebSocketResponse, meta: Meta, command: str = None, message_json: Dict[str, str] = None):
        if not command == CommandType.history:
            raise UnsuitableCommand
        
        try:
            room = message_json['room']
            n = message_json['n']

        except:
            raise BadRequest

        if room is None:
            room = ''

        if room == '':
            if not meta.loggedin:
                raise NoRegistredUserFound
            
            await NotificationStore().history_user(ws=ws_response, user=UserStore().get_user(username=meta.user_name), n=n)
            return meta
        
        await NotificationStore().history_room(ws=ws_response, user_name=meta.user_name, room=RoomStore().get_room_by_name(room_name=room), n=n)

        return meta