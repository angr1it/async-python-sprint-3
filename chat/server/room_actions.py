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
    BadRequest,
    DialogueOpenedAlready,
    UnknownError,
    NoRegistredUserFound
)

from .state.meta import Meta
from .state.room import RoomStore, Room, RoomType
from .state.user import UserStore

from .state.message import (
    NotificationStore,
    CreateRoom as CreateRoomNotification,
    CreateRoomAnon as CreateRoomAnonNotification,
    DeleteRoom as DeleteRoomNotification,
    AddUser as AddUserNotification,
    RemoveUser as RemoveUserNotification,
    JoinRoom as JoinRoomNotification,
    LeaveRoom as LeaveRoomNotification
)
from .command import Command

NO_AUTH = 'Not authorized.'
NOT_ALLOWED_TO_JOIN = 'Not allowed to join this room.'
NOT_ALLOWED = 'Not allowed.'
class JoinRoom(Command):
    
    @classmethod
    async def run(cls, ws_response: web.WebSocketResponse, meta: Meta, command: str = None, message_json: Dict[str, str] = None):
 
        if not command == CommandType.join_room:
            raise UnsuitableCommand
        
        try:
            room_str = message_json['room_name']
        except:
            raise BadRequest
        
        try:
            if RoomStore().join(user=UserStore().get_user(meta.user_name), room=RoomStore().get_room_by_name(room_str)):
                await NotificationStore().process(
                    ws=ws_response,
                    notification=JoinRoomNotification(
                        action=CommandType.join_room,
                        datetime=datetime.now(),
                        expired=False,
                        success=True,
                        reason='',
                        room_name=room_str,
                        user_name=meta.user_name
                    )
                )
                return meta
        
        except NoRegistredUserFound:
            pass

        await NotificationStore().process(
            ws=ws_response,
            notification=JoinRoomNotification(
                action=CommandType.join_room,
                datetime=datetime.now(),
                expired=False,
                success=False,
                reason=NOT_ALLOWED_TO_JOIN,
                room_name=room_str,
                user_name=meta.user_name
            )
        )

        return meta

class LeaveRoom(Command):
    @classmethod
    async def run(cls,ws_response: web.WebSocketResponse, meta: Meta, command: str = None, message_json: Dict[str, str] = None):
        if not command == CommandType.leave_room:
            raise UnsuitableCommand
        
        try:
            room_name = message_json['room_name']
        except:
            raise BadRequest
        
        if RoomStore().user_in_room(
            user=UserStore().get_user(meta.user_name),
            room=RoomStore().get_room_by_name(room_name)
        ):
            await NotificationStore().process(
                ws=ws_response,
                notification=LeaveRoomNotification(
                    action=CommandType.leave_room,
                    datetime=datetime.now(),
                    expired=False,
                    success=True,
                    reason='',
                    room_name=room_name,
                    user_name=meta.user_name
                )
            )
            RoomStore().leave(
                user=UserStore().get_user(meta.user_name),
                room=RoomStore().get_room_by_name(room_name)
            )

            return meta
        else:
            raise UnknownError

class CreateRoom(Command):
    @classmethod
    async def run(cls, ws_response: web.WebSocketResponse, meta: Meta, command: str = None, message_json: Dict[str, str] = None):
        if not command == CommandType.create_room:
            raise UnsuitableCommand
        
        try:
            room_name = message_json['room_name']
            room_type = RoomType(message_json['room_type'])
        except:
            raise BadRequest
        
        # See OpenDialogue
        if room_type == RoomType.private:
            raise BadRequest
        
        if not meta.loggedin:
            await NotificationStore().process(
                ws=ws_response,
                notification=CreateRoomAnonNotification(
                    action=CommandType.create_room,
                    datetime=datetime.now(),
                    expired=False,
                    success=False,
                    reason=NO_AUTH,
                    room_name=room_name
                )
            )

            return meta

        try:
            room = RoomStore().add_room(
                room=Room(
                    key=uuid.uuid4(),
                    name=room_name,
                    room_type=room_type,
                    admins=[meta.user_name],
                    allowed=[meta.user_name],
                    deleted=False
                )
            )
            
            await NotificationStore().process(
                ws=ws_response,
                notification=CreateRoomNotification(
                    action=CommandType.create_room,
                    datetime=datetime.now(),
                    expired=False,
                    success=True,
                    reason='',
                    user_name=meta.user_name,
                    room_name=room.name,
                    admins=room.admins,
                    allowed=room.allowed
                )
            )
        except:
            raise UnknownError
        
        return meta

class DeleteRoom(Command):
    @classmethod
    async def run(cls, request: Request, ws_response: web.WebSocketResponse, meta: Meta, command: str = None, message_json: Dict[str, str] = None):
        if not command == CommandType.delete_room:
            raise UnsuitableCommand
        
        try:
            room_name = message_json['room_name']
        except:
            # send the message, return
            raise NotImplementedError
        
        try:
            RoomStore().delete_room(
                app=request.app,
                room=RoomStore().get_room_by_name(room_name=room_name),
                admin=UserStore().get_user(username=meta.user_name)
            )

            NotificationStore().process(
                app=request.app,
                notification=DeleteRoomNotification(CommandType.delete_room, datetime.now(), meta.user_name, True, '', room_name)
            )
        except:
            raise NotImplementedError
        
        return meta
    
class AddUser(Command):
    @classmethod
    async def run(cls, ws_response: web.WebSocketResponse, meta: Meta, command: str = None, message_json: Dict[str, str] = None):
        if not command == CommandType.add_user:
            raise UnsuitableCommand
        
        try:
            room_name = message_json['room_name']
            new_user = message_json['new_user']
        except:
            raise BadRequest
        try:
            if (RoomStore().add_user_to_room(
                    room=RoomStore().get_room_by_name(room_name),
                    admin=UserStore().get_user(meta.user_name),
                    new_user=UserStore().get_user(new_user)
                )):
                await NotificationStore().process(
                    ws=ws_response,
                    notification=AddUserNotification(
                        action=CommandType.add_user,
                        datetime=datetime.now(),
                        expired=False,
                        success=True,
                        reason='',
                        user_name=meta.user_name,
                        room_name=room_name,
                        new_user=new_user
                    )
                )
                return meta
        
        except NoRegistredUserFound:
            await NotificationStore().process(
                ws=ws_response,
                notification=AddUserNotification(
                    action=CommandType.add_user,
                    datetime=datetime.now(),
                    expired=False,
                    success=False,
                    reason=NO_AUTH,
                    user_name=meta.user_name,
                    room_name=room_name,
                    new_user=new_user
                )
            )
            return meta
        
        await NotificationStore().process(
            ws=ws_response,
            notification=AddUserNotification(
                action=CommandType.add_user,
                datetime=datetime.now(),
                expired=False,
                success=False,
                reason=NOT_ALLOWED,
                user_name=meta.user_name,
                room_name=room_name,
                new_user=new_user
            )
        )
        
        return meta

class RemoveUser(Command):
    @classmethod
    async def run(cls, ws_response: web.WebSocketResponse, meta: Meta, command: str = None, message_json: Dict[str, str] = None):
        if not command == CommandType.remove_user:
            raise UnsuitableCommand
        
        try:
            room_name = message_json['room_name']
            remove_user = message_json['remove_user']
        except:
            raise BadRequest
        
        try:
            if not RoomStore().remove_user_from_room(
                room=RoomStore().get_room_by_name(room_name),
                admin=UserStore().get_user(meta.user_name),
                remove_user=UserStore().get_user(remove_user)
            ):
                raise ValueError

            await NotificationStore().process(
                ws=ws_response,
                notification=RemoveUserNotification(
                    action=CommandType.remove_user, 
                    datetime=datetime.now(),
                    expired=False,
                    success=True,
                    reason='',
                    user_name=meta.user_name,
                    room_name=room_name,
                    remove_user=remove_user
                )
            )

            return meta

        except:
            await NotificationStore().process(
                ws=ws_response,
                notification=RemoveUserNotification(
                    action=CommandType.remove_user, 
                    datetime=datetime.now(),
                    expired=False,
                    success=False,
                    reason=NOT_ALLOWED,
                    user_name=meta.user_name,
                    room_name=room_name,
                    remove_user=remove_user
                )
            )
        
        return meta

class OpenDialogue(Command):
    @classmethod
    async def run(cls, request: Request, ws_response: web.WebSocketResponse, meta: Meta, command: str = None, message_json: Dict[str, str] = None):
        if not command == CommandType.open_dialogue:
            raise UnsuitableCommand
        
        try:
            user_name = message_json['user_name']
        except:
            raise NotImplementedError
        
        try:
            room = RoomStore().add_room(
                app=request.app,
                room=Room(
                    key=uuid.uuid4,
                    name='',
                    room_type=RoomType.private,
                    admins=[UserStore().get_user(meta.user_name), UserStore().get_user(user_name)],
                    allowed=[UserStore().get_user(meta.user_name), UserStore().get_user(user_name)]
                )
            )

            NotificationStore().process(
                app=request.app,
                notification=CreateRoomNotification(CommandType.open_dialogue, datetime.now(), meta.user_name, True, 'Private message', user_name, room.key)
            )

            NotificationStore().process(
                app=request.app,
                notification=CreateRoomNotification(CommandType.open_dialogue, datetime.now(), user_name, True, 'Private message', meta.user_name, room.key)
            )
        except DialogueOpenedAlready:
            await NotificationStore().process(
                ws=ws_response,
                notification=CreateRoomNotification(
                    action=CommandType.create_room,
                    datetime=datetime.now(),
                    expired=False,
                    success=False,
                    reason='Dialogue opened already.',
                    user_name=meta.user_name,
                    room_name=room.name
                )
            )
        except:
            raise UnknownError
        
        return meta