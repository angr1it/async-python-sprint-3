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
    BadRequest,
    DialogueOpenedAlready,
    UnknownError,
    NoRegistredUserFound,
    NotAuthorized,
    NoRoomFound,
    NoRoomAccessError
)

from .state.meta import Meta
from .state.room import RoomStore, Room, RoomType
from .state.user import UserStore

from .state.message import (
    NotificationStore,
    CreateRoomNotification,
    CreateRoomAnonNotification,
    DeleteRoomNotification,
    AddUserNotification,
    RemoveUserNotification,
    JoinRoomNotification,
    LeaveRoomNotification,
    OpenDialogueNotification,
    DeleteDialogueNotification
)
from .command import Command

NO_AUTH = 'Not authorized.'
NOT_ALLOWED_TO_JOIN = 'Not allowed to join this room.'
NOT_ALLOWED = 'Not allowed.'
DIALOGUE_OPENED_ERR = 'Dialogue opened already.'
NO_DIALOGUE = 'No dialogue found.'



class JoinRoomAction(Command):
    
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

class LeaveRoomAction(Command):
    @classmethod
    async def run(cls,ws_response: web.WebSocketResponse, meta: Meta, command: str = None, message_json: Dict[str, str] = None):
        if not command == CommandType.leave_room:
            raise UnsuitableCommand
        
        try:
            room_name = message_json['room_name']
        except:
            raise BadRequest
        
        if RoomStore().user_in_room(
            username=meta.user_name,
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
            raise NoRegistredUserFound

class CreateRoomAction(Command):
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

        
        return meta

class DeleteRoomAction(Command):
    @classmethod
    async def run(cls, ws_response: web.WebSocketResponse, meta: Meta, command: str = None, message_json: Dict[str, str] = None):
        if not command == CommandType.delete_room:
            raise UnsuitableCommand
        
        try:
            room_name = message_json['room_name']
        except:
            raise BadRequest
        
        try:
            RoomStore().delete_room(
                room=RoomStore().get_room_by_name(room_name=room_name),
                admin=UserStore().get_user(username=meta.user_name)
            )

            await NotificationStore().process(
                ws=ws_response,
                notification=DeleteRoomNotification(
                    action=CommandType.delete_room,
                    datetime=datetime.now(),
                    expired=False,
                    success=True,
                    reason='',
                    user_name=meta.user_name,
                    room_name=room_name
                )
            )
        except (NotAuthorized, NoRegistredUserFound):
            await NotificationStore().process(
                ws=ws_response,
                notification=DeleteRoomNotification(
                    action=CommandType.delete_room,
                    datetime=datetime.now(),
                    expired=False,
                    success=False,
                    reason=NO_AUTH,
                    user_name=meta.user_name,
                    room_name=room_name
                )
            )
        
        return meta
    
class AddUserAction(Command):
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

class RemoveUserAction(Command):
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

class OpenDialogueAction(Command):
    @classmethod
    async def run(cls, ws_response: web.WebSocketResponse, meta: Meta, command: str = None, message_json: Dict[str, str] = None):

        if not command == CommandType.open_dialogue:
            raise UnsuitableCommand
        
        try:
            with_user = message_json['with_user']
        except:
            raise BadRequest
        
        if not meta.loggedin:
            raise NoRegistredUserFound
        
        try:
            room = RoomStore().add_room(
                room=Room(
                    key=uuid.uuid4,
                    name='',
                    room_type=RoomType.private,
                    admins=[meta.user_name, with_user],
                    allowed=[meta.user_name, with_user],
                    deleted=False
                )
            )

            await NotificationStore().process(
                ws=ws_response,
                notification=OpenDialogueNotification(
                    action=CommandType.open_dialogue,
                    datetime=datetime.now(),
                    expired=False,
                    success=True,
                    reason='',
                    user_name=meta.user_name,
                    users=room.admins
                )
            )
            await NotificationStore().process(
                ws=ws_response,
                notification=OpenDialogueNotification(
                    action=CommandType.open_dialogue,
                    datetime=datetime.now(),
                    expired=False,
                    success=True,
                    reason='',
                    user_name=with_user,
                    users=room.admins
                )
            )

        except DialogueOpenedAlready:
            await NotificationStore().process(
                ws=ws_response,
                notification=OpenDialogueNotification(
                    action=CommandType.open_dialogue,
                    datetime=datetime.now(),
                    expired=False,
                    success=False,
                    reason=DIALOGUE_OPENED_ERR,
                    user_name=meta.user_name,
                    users=room.admins
                )
            )
        except NotAuthorized:
            await NotificationStore().process(
                ws=ws_response,
                notification=OpenDialogueNotification(
                    action=CommandType.open_dialogue,
                    datetime=datetime.now(),
                    expired=False,
                    success=False,
                    reason=NO_AUTH,
                    user_name=meta.user_name,
                    users=room.admins
                )
            )
        
        return meta

class DeleteDialogueAction(Command):
    @classmethod
    async def run(cls, ws_response: web.WebSocketResponse, meta: Meta, command: str = None, message_json: Dict[str, str] = None):
        if not command == CommandType.delete_dialogue:
            raise UnsuitableCommand
        
        try:
            with_user = message_json['with_user']
        except:
            raise NotImplementedError
        
        if not meta.loggedin:
            raise NoRegistredUserFound
        
        try:
            room = RoomStore().find_private_room(
                user1=UserStore().get_user(with_user),
                user2=UserStore().get_user(meta.user_name)
            )

            if room is None:
                raise NoRoomFound
            
            users = room.admins.copy()

            RoomStore().delete_room(room=room, admin=UserStore().get_user(meta.user_name))

            await NotificationStore().process(
                ws=ws_response,
                notification=DeleteDialogueNotification(
                    action=CommandType.delete_dialogue,
                    datetime=datetime.now(),
                    expired=False,
                    success=True,
                    reason='',
                    user_name=meta.user_name,
                    users=users
                )
            )
            await NotificationStore().process(
                ws=ws_response,
                notification=DeleteDialogueNotification(
                    action=CommandType.delete_dialogue,
                    datetime=datetime.now(),
                    expired=False,
                    success=True,
                    reason='',
                    user_name=with_user,
                    users=users
                )
            )
        except NoRoomFound:
            await NotificationStore().process(
                ws=ws_response,
                notification=DeleteDialogueNotification(
                    action=CommandType.delete_dialogue,
                    datetime=datetime.now(),
                    expired=False,
                    success=False,
                    reason=NO_DIALOGUE,
                    user_name=meta.user_name,
                    users=[]
                )
            )

        return meta