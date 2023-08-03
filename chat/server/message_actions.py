from typing import List, Dict, Tuple, Union
from aiohttp import ClientWebSocketResponse
import logging
from datetime import datetime
import dataclasses
from aiohttp import web
from aiohttp.web_request import Request
import aiofiles
from datetime import datetime
import asyncio
import json

import uuid

logger = logging.getLogger()

from ..command_types import CommandType


from ..exceptions import (
    UnsuitableCommand,
    CommandArgError,
    EmptyCommand,
    BadRequest
)

from .state.meta import Meta
from .state.room import RoomStore
from .state.user import UserStore
from .state.message import NotificationStore, Message
from .command import Command



class Send(Command):
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
        
        
        if private:
            try:
                NotificationStore().process(
                    ws=ws_response,
                    notification=Message(
                        action=CommandType.send,
                        datetime=datetime.now(),
                        room_key=RoomStore().find_private_room(user1=UserStore().get_user(meta.user_name), user2=UserStore().get_user(to_user)).key,
                        user_name=meta.user_name,
                        to=to_user,
                        private=True,
                        message_str=message
                    )
                )
            except:
                raise NotImplementedError
            
            return meta
        
        try:
            await NotificationStore().process(
                ws=ws_response,
                notification=Message(
                    action=CommandType.send,
                    datetime=datetime.now(),
                    room_name=room_name,
                    user_name=meta.user_name,
                    to=to_user,
                    private=False,
                    message_str=message,
                    expired=False,
                    success=True,
                    reason=''
                )
            )

        except:
            raise NotImplementedError

        return meta
    

class History(Command):
    @classmethod
    async def run(cls, ws_response: web.WebSocketResponse, meta: Meta, command: str = None, message_json: Dict[str, str] = None):
        if not command == CommandType.history:
            raise UnsuitableCommand
        
        try:
            room = message_json['room']
            n = message_json['n']

        except:
            raise BadRequest

        await NotificationStore().history(ws=ws_response, room=RoomStore().get_room_by_name(room_name=room), n=n)

        return meta