from dataclasses import dataclass
import dataclasses
import json
from typing import List, Dict
import logging
import asyncio
from datetime import datetime
from aiohttp import web

import uuid

from ...singleton import singleton
from ...command_types import CommandType

from .room import Room, RoomStore, RoomType
from .user import UserStore
from ...exceptions import *

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from dataclasses import dataclass
from abc import ABC, abstractmethod


@dataclass
class Action(ABC):
    action: str
    datetime: float
    expired: bool

    success: bool
    reason: str

    @abstractmethod
    def get_notification(self) -> dict:
        raise NotImplementedError('get_notification must be overrided in the child class!')
    
    def _command_type_check(self, expected: str):
        if self.action == expected:
                return
            
        raise ValueError(f"Message's action string must be equal to {expected}! Current: {self.action}")

@dataclass
class UserAction(Action):
    user_name: str

@dataclass
class RoomAction(Action):
    room_name: str
    user_name: str

@dataclass
class Message(RoomAction):
    to: str
    
    private: bool
    message_str: str
    
    def __post_init__(self):
        self._command_type_check(CommandType.send)

    def get_notification(self):
        return {'action': self.action, 'datetime': str(self.datetime), 'private': self.private, 'room': self.room_name, 'from': self.user_name, 'to': self.to, 'message': self.message_str}

@dataclass
class JoinRoom(RoomAction):
    
    def __post_init__(self):
        self._command_type_check(CommandType.join_room)

    def get_notification(self):
        return {'action': CommandType.join_room, 'success': self.success, 'reson': self.reason, 'datetime': str(self.datetime), 'user': self.user_name, 'room_name': self.room_name}

@dataclass
class Login(UserAction):

    def __post_init__(self):
        self._command_type_check(CommandType.login)
    
    def get_notification(self) -> dict:
        return {'action': CommandType.login, 'success': self.success, 'datetime': str(self.datetime), 'user': self.user_name, 'reason': self.reason}

@dataclass
class Logout(UserAction):

    def __post_init__(self):
        self._command_type_check(CommandType.logout)
    
    def get_notification(self) -> dict:
        return {'action': CommandType.logout, 'success': self.success, 'datetime': str(self.datetime), 'user': self.user_name, 'reason': self.reason}
    
@dataclass
class Register(Action):

    username: str

    def __post_init__(self):
        self._command_type_check(CommandType.register)
    
    def get_notification(self) -> dict:
        return {'action': CommandType.register, 'datetime': str(self.datetime),  'success': self.success, 'user': self.username, 'reason': self.reason}

@dataclass
class FileLoaded(UserAction):

    def __post_init__(self):
        self._command_type_check(CommandType.publish_file)
    
    def get_notification(self) -> dict:
        return {'action': CommandType.publish_file, 'success': self.success, 'publisher': self.publisher}

@dataclass
class FilePublished(UserAction):

    publisher: str
    key: str

    def __post_init__(self):
        self._command_type_check(CommandType.publish_file)
    
    def get_notification(self) -> dict:
        return {'action': CommandType.publish_file, 'publisher': self.publisher, 'key': self.key, 'datetime': self.datetime}

@dataclass
class GetRoomHistory(Action):

    messages: List[Dict]

    def __post_init__(self):
        self._command_type_check(CommandType.history)
    
    def get_notification(self) -> dict:
        return {'action': CommandType.history, 'datetime': str(self.datetime), 'success': self.success, 'reason': self.reason, 'messages': self.messages}

@dataclass
class CreateRoom(UserAction):

    room_name: str
    admins: list[str]
    allowed: list[str]

    def __post_init__(self):
        self._command_type_check(CommandType.create_room)

    def get_notification(self) -> dict:
        return {'action': CommandType.create_room, 'datetime': str(self.datetime), 'success': self.success, 'reason': self.reason, 'room_name': self.room_name, 'admins': self.admins, 'allowed': self.allowed}

@dataclass
class CreateRoomAnon(Action):

    room_name: str

    def __post_init__(self):
        self._command_type_check(CommandType.create_room)

    def get_notification(self) -> dict:
        return {'action': CommandType.create_room, 'datetime': str(self.datetime), 'success': self.success, 'reason': self.reason, 'room_name': self.room_name}

@dataclass
class DeleteRoom(UserAction):

    room_name: str

    def __post_init__(self):
        self._command_type_check(CommandType.delete_room)

    def get_notification(self) -> dict:
        return {'action': CommandType.delete_room, 'datetime': str(self.datetime), 'success': self.success, 'reason': self.reason, 'room_name': self.room_name}

@dataclass
class AddUser(UserAction):

    room_name: str
    new_user: str

    def __post_init__(self):
        self._command_type_check(CommandType.add_user)

    def get_notification(self) -> dict:
        return {'action': CommandType.add_user, 'datetime': str(self.datetime), 'success': self.success, 'reason': self.reason, 'room_name': self.room_name, 'new_user': self.new_user}

@dataclass
class RemoveUser(UserAction):

    room_name: str
    remove_user: str

    def __post_init__(self):
        self._command_type_check(CommandType.remove_user)

    def get_notification(self) -> dict:
        return {'action': CommandType.remove_user, 'datetime': str(self.datetime), 'success': self.success, 'reason': self.reason, 'room_name': self.room_name, 'remove_user': self.remove_user}

@dataclass
class ConnectAnon(Action):
    name: str

    def __post_init__(self):
        self._command_type_check(CommandType.connected)
    
    def get_notification(self) -> dict:
        return {'action': CommandType.connected, 'datetime': str(self.datetime), 'success': self.success, 'reason': self.reason, 'name': self.name}

@dataclass
class AnyError(Action):

    def __post_init__(self):
        self._command_type_check(CommandType.error)

    def get_notification(self) -> dict:
        return {'action': CommandType.error, 'datetime': str(self.datetime), 'reason': self.reason}

@dataclass
class LeaveRoom(RoomAction):

    def __post_init__(self):
        self._command_type_check(CommandType.leave_room)

    def get_notification(self) -> dict:
        return {'action': CommandType.leave_room, 'datetime': str(self.datetime), 'success': self.success, 'reason': self.reason, 'room_name': self.room_name, 'user_name': self.user_name}

@singleton
class NotificationStore:  
    def __init__(self) -> None:
        
        self.store = {}

        self.store['users'] = {}
        self.store['rooms'] = {}
        self.store['other'] = list()

    def __add(self, action: Action):

        if issubclass(type(action), UserAction):
            try:
                self.store['users'][action.username].append(action)
            except KeyError:
                self.store['users'][action.username] = list()
                self.store['users'][action.username].append(action)
            finally:
                return
        
        if issubclass(type(action), RoomAction):

            try:
                self.store['rooms'][RoomStore().get_room_by_name(action.room_name).key].append(action)
            except KeyError:
                self.store['rooms'][RoomStore().get_room_by_name(action.room_name).key] = list()
                self.store['rooms'][RoomStore().get_room_by_name(action.room_name).key].append(action)
            return

        self.store['other'].append(action)

    async def __send(self, ws: web.WebSocketResponse, mssg: dict):
        await ws.send_json(mssg)
     
    async def process(self, ws: web.WebSocketResponse, notification: Action):

        if issubclass(type(notification), RoomAction):
            if not RoomStore().user_in_room(
                user=UserStore().get_user(username=notification.user_name),
                room=RoomStore().get_room_by_name(room_name=notification.room_name)
            ):
                raise NoRoomAccessError

        self.__add(notification)
        await self.__send(ws=ws, mssg=notification.get_notification())

    def get_n_messages(self, room: Room, n: int = 20) -> list:
        try:
            messages = [message.get_notification() for message in self.store['rooms'][room.key]][:n]
            return messages
        except:
            raise NoRoomFound
    
    async def history(self, ws: web.WebSocketResponse, room: Room, n: int = 20) -> bool:
        
        if room is None:
            return ValueError
        
        await self.process(   
            ws=ws,
            notification=GetRoomHistory(
                action=CommandType.history,
                datetime=datetime.now(),
                success=True,
                reason='',
                messages=self.get_n_messages(room=room, n=n),
                expired=False
            )
        )
   
        return True

    async def dump(self):
        pass

    async def load(self):
        pass