from typing import List, Dict
import logging
from datetime import datetime

from pydantic.dataclasses import dataclass
from pydantic.tools import parse_obj_as
import dataclasses
import json


from ...singleton import singleton
from ...command_types import CommandType
from ...utils.my_response import WSResponse

from .room import Room, RoomStore
from .user import UserStore, User
from ...exceptions import (
    NoRegistredUserFound,
    NoRoomFound
)
from ...manage_files import read_file, write_file

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from abc import ABC


@dataclass
class Action(ABC):
    action: str
    datetime: str
    expired: bool
    
    success: bool
    reason: str

    payload: Dict

    def get_notification(self) -> Dict:
        return {'action': self.action, 'datetime': self.datetime, 'success': self.success, 'reason': self.reason, 'payload': self.payload}

@dataclass
class UserAction(Action):
    user_name: str

    def get_notification(self) -> Dict:
        return {'action': self.action, 'success': self.success, 'reason': self.reason, 'datetime': self.datetime, 'user': self.user_name, 'payload': self.payload}

@dataclass
class RoomAction(Action):
    room_name: str
    user_name: str

    def get_notification(self) -> Dict:
        return {'action': self.action, 'success': self.success, 'reason': self.reason, 'datetime': self.datetime, 'user': self.user_name, 'room_name': self.room_name, 'payload': self.payload}

@dataclass
class FilePublished(UserAction):

    publisher: str
    key: str

    def __post_init__(self):
        self._command_type_check(CommandType.publish_file)
    
    def get_notification(self) -> Dict:
        return {'action': CommandType.publish_file, 'publisher': self.publisher, 'key': self.key, 'datetime': self.datetime}


@dataclass
class AnyError(Action):

    def __post_init__(self):
        self._command_type_check(CommandType.error)

    def get_notification(self) -> Dict:
        return {'action': CommandType.error, 'datetime': self.datetime, 'reason': self.reason}

def get_connected_notification(name: str) -> Action:
    return Action(
        action=CommandType.connected,
        datetime=str(datetime.now()),
        expired=False,
        success=True,
        reason='',
        payload={
            'user_name': name
        }  
    )

def get_message_notification(room_name, user_name, success, reason, private, to, message):
        return RoomAction(
            action=CommandType.send,
            datetime=str(datetime.now()),
            expired=False,
            success=success,
            reason=reason,
            room_name=room_name,
            user_name=user_name,
            payload={
                'private': private,
                'to': to,
                'message': message
            }
        )

def get_history_notification(user_name: str, success: bool, reason: str, payload) -> UserAction:
    return UserAction(
        action=CommandType.history,
        datetime=str(datetime.now()),
        expired=False,
        success=success,
        reason=reason,
        payload={
            'history': payload
        },
        user_name=user_name
    )

def get_error_message(reason):
    return Action(
        action=CommandType.error,
        datetime=str(datetime.now()),
        expired=False,
        success=False,
        reason=reason,
        payload={}
    )

@singleton
class NotificationStore:  
    def __init__(self) -> None:
        
        self.store = {}

        self.store['users'] = {}
        self.store['rooms'] = {}
        self.store['other'] = list()

    def __add(self, action: Action):

        if issubclass(type(action), UserAction):
            if action.action == CommandType.history:
                return
            
            try:
                self.store['users'][action.user_name].append(action)
            except KeyError:
                self.store['users'][action.user_name] = list()
                self.store['users'][action.user_name].append(action)
            finally:
                return
        
        if issubclass(type(action), RoomAction):
            if action.payload['private']:
                room = RoomStore().find_private_room(
                    user1=UserStore().get_user(action.user_name),
                    user2=UserStore().get_user(action.payload['to'])
                )
            else:
                room = RoomStore().get_room_by_name(action.room_name)
                
            try:
                self.store['rooms'][room.key].append(action)
            except KeyError:
                self.store['rooms'][room.key] = list()
                self.store['rooms'][room.key].append(action)
            return

        self.store['other'].append(action)

    async def __send(self, ws: WSResponse, mssg: Dict):
        await ws.send_json(mssg)
     
    async def process(self, ws: WSResponse, notification: Action):

        if issubclass(type(notification), RoomAction):
            try:
                if notification.payload['private']:
                    if not RoomStore().user_in_room(
                        username=notification.user_name,
                        room=RoomStore().find_private_room(
                            user1=UserStore().get_user(notification.user_name),
                            user2=UserStore().get_user(notification.payload['to'])
                        )
                    ):
                        raise NoRegistredUserFound
                else:
                    if not RoomStore().user_in_room(
                        username=notification.user_name,
                        room=RoomStore().get_room_by_name(room_name=notification.room_name)
                    ):
                        raise NoRegistredUserFound
            except Exception as ex:
                logger.error(ex)   
                raise NoRegistredUserFound

        self.__add(notification)
        await self.__send(ws=ws, mssg=notification.get_notification())

    def get_n_messages(self, room: Room, n: int = 20) -> List:
        try:
            messages = [message.get_notification() for message in self.store['rooms'][room.key]][:n]
            return messages
        except:
            raise NoRoomFound
    
    def get_n_notifications_user(self, user: User, n: int = 20) -> List:
        try:
            notifications = [notification.get_notification() for notification in self.store['users'][user.username]][:n]
            return notifications
        except:
            raise NoRegistredUserFound
        
    async def history_room(self, ws: WSResponse, user_name: str,  room: Room, n: int = 20) -> bool:
        
        if room is None:
            return ValueError
        
        await self.process(
            ws=ws,
            notification=get_history_notification(
                user_name=user_name,
                success=True,
                reason='',
                payload=self.get_n_messages(room=room, n=n),
            )
        )
   
        return True

    async def history_user(self, ws: WSResponse, user: User, n: int = 20) -> bool:
        
        if user is None:
            return ValueError
        
        await self.process(
            ws=ws,
            notification=get_history_notification(
                user_name=user.username,
                success=True,
                reason='',
                payload=self.get_n_notifications_user(user=user, n=n)
            )
        )
   
        return True
    
    def __store_to_dict(self):
        data = dict()
        data['users'] = dict()
        data['rooms'] = dict()
        data['other'] = list()

        for user, user_data in self.store['users'].items():
            data['users'][user] = [dataclasses.asdict(d) for d in user_data]

        for room, room_data in self.store['rooms'].items():
            data['rooms'][str(room)] = [dataclasses.asdict(d) for d in room_data]

        data['other'] = [dataclasses.asdict(d) for d in self.store['other']]

        return json.dumps(data, indent=4, sort_keys=True, default=str)
    
    async def dump(self, path: str = './data/messages.json') -> bool:
        """
        Dumps all the data necessary for future load.
        """
        
        store = self.__store_to_dict()

        await write_file(path, store)

        return True
    
    async def load(self, path: str = './data/messages.json'):
        try:
            data = await read_file(path)

            for _, user in data['rooms'].items():
                for user_data in user:
                    self.__add(parse_obj_as(RoomAction, user_data))

            for _, user in data['users'].items():
                for user_data in user:
                    self.__add(parse_obj_as(UserAction, user_data))
            
            for other_data in data['other']:
                self.__add(parse_obj_as(Action, other_data))
            
        except Exception as ex:
            logger.error(f'Unable load users from {path}, because: {ex}.')