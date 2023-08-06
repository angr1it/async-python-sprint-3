from typing import Dict
import logging
from datetime import datetime
from datetime import datetime

logger = logging.getLogger()

from ..utils.my_response import WSResponse
from ..command_types import CommandType
from ..exceptions import (
    UnsuitableCommand,
    BadRequest,
    DialogueOpenedAlready,
    NoRegistredUserFound,
    NotAuthorized,
    NoRoomFound,
)
from .state.meta import Meta
from .state.room import RoomStore, Room, RoomType
from .state.user import UserStore
from .state.message import (
    NotificationStore,
    UserAction
)
from .command import Command

NO_AUTH = 'Not authorized.'
NOT_ALLOWED_TO_JOIN = 'Not allowed to join this room.'
NOT_ALLOWED = 'Not allowed.'
DIALOGUE_OPENED_ERR = 'Dialogue opened already.'
NO_DIALOGUE = 'No dialogue found.'



class JoinRoomAction(Command):
    
    @staticmethod
    def get_join_room_notification(user_name: str, room_name: str, success: bool, reason: str):
        return UserAction(
            action=CommandType.join_room,
            datetime=str(datetime.now()),
            expired=False,
            success=success,
            reason=reason,
            user_name=user_name,
            payload={
                'room_name': room_name
            }
        )

    @classmethod
    async def run(cls, ws_response: WSResponse, meta: Meta, command: str = None, message_json: Dict[str, str] = None):
 
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
                    notification=JoinRoomAction.get_join_room_notification(user_name=meta.user_name, room_name=room_str, success=True, reason='')
                )
                return meta
        
        except NoRegistredUserFound:
            pass

        await NotificationStore().process(
            ws=ws_response,
            notification=JoinRoomAction.get_join_room_notification(user_name=meta.user_name, room_name=room_str, success=False, reason=NOT_ALLOWED_TO_JOIN)
        )

        return meta

class LeaveRoomAction(Command):

    @staticmethod
    def get_leave_room_notification(user_name: str, room_name: str, success: bool, reason: str):
        return UserAction(
            action=CommandType.leave_room,
            datetime=str(datetime.now()),
            expired=False,
            success=success,
            reason=reason,
            user_name=user_name,
            payload={
                'room_name': room_name
            }
        )
    
    @classmethod
    async def run(cls,ws_response: WSResponse, meta: Meta, command: str = None, message_json: Dict[str, str] = None):
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
                notification=LeaveRoomAction.get_leave_room_notification(user_name=meta.user_name, room_name=room_name, success=True, reason='')
            )
            RoomStore().leave(
                user=UserStore().get_user(meta.user_name),
                room=RoomStore().get_room_by_name(room_name)
            )

            return meta
        else:
            raise NoRegistredUserFound

class CreateRoomAction(Command):

    @staticmethod
    def get_create_room_notification(user_name: str, room_name: str, success: bool, reason: str):
        return UserAction(
            action=CommandType.create_room,
            datetime=str(datetime.now()),
            expired=False,
            success=success,
            reason=reason,
            user_name=user_name,
            payload={
                'room_name': room_name
            }
        )

    @classmethod
    async def run(cls, ws_response: WSResponse, meta: Meta, command: str = None, message_json: Dict[str, str] = None):
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
                notification=CreateRoomAction.get_create_room_notification(user_name=meta.user_name, room_name=room_name, success=False, reason=NO_AUTH)
            )

            return meta

        room = RoomStore().add_room(
            room=Room(
                key=None,
                name=room_name,
                room_type=room_type,
                admins=[meta.user_name],
                allowed=[meta.user_name],
                deleted=False
            )
        )
        
        await NotificationStore().process(
            ws=ws_response,
            notification=CreateRoomAction.get_create_room_notification(user_name=meta.user_name, room_name=room_name, success=True, reason='')
        )
        
        return meta

class DeleteRoomAction(Command):

    @staticmethod
    def get_delete_room_notification(user_name: str, room_name: str, success: bool, reason: str):
        return UserAction(
            action=CommandType.delete_room,
            datetime=str(datetime.now()),
            expired=False,
            success=success,
            reason=reason,
            user_name=user_name,
            payload={
                'room_name': room_name
            }
        )
    
    @classmethod
    async def run(cls, ws_response: WSResponse, meta: Meta, command: str = None, message_json: Dict[str, str] = None):
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
                notification=DeleteRoomAction.get_delete_room_notification(user_name=meta.user_name, room_name=room_name, success=True, reason='')
            )
        except (NotAuthorized, NoRegistredUserFound):
            await NotificationStore().process(
                ws=ws_response,
                notification=DeleteRoomAction.get_delete_room_notification(user_name=meta.user_name, room_name=room_name, success=False, reason=NO_AUTH)
            )
        
        return meta
    
class AddUserAction(Command):

    @staticmethod
    def get_add_user_notification(user_name: str, room_name: str, new_user: str, success: bool, reason: str):
        return UserAction(
            action=CommandType.add_user,
            datetime=str(datetime.now()),
            expired=False,
            success=success,
            reason=reason,
            user_name=user_name,
            payload={
                'room_name': room_name,
                'new_user': new_user
            }
        )
    
    @classmethod
    async def run(cls, ws_response: WSResponse, meta: Meta, command: str = None, message_json: Dict[str, str] = None):
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
                    notification=AddUserAction.get_add_user_notification(user_name=meta.user_name, room_name=room_name, new_user=new_user, success=True, reason='')
                )
                return meta
        
        except NoRegistredUserFound:
            await NotificationStore().process(
                ws=ws_response,
                notification=AddUserAction.get_add_user_notification(user_name=meta.user_name, room_name=room_name, new_user=new_user, success=False, reason=NO_AUTH)
            )
            return meta
        
        await NotificationStore().process(
            ws=ws_response,
            notification=AddUserAction.get_add_user_notification(user_name=meta.user_name, room_name=room_name, new_user=new_user, success=False, reason=NOT_ALLOWED)
        )
        
        return meta

class RemoveUserAction(Command):

    @staticmethod
    def get_remove_user_notification(user_name: str, room_name: str, remove_user: str, success: bool, reason: str):
        return UserAction(
            action=CommandType.remove_user,
            datetime=str(datetime.now()),
            expired=False,
            success=success,
            reason=reason,
            user_name=user_name,
            payload={
                'room_name': room_name,
                'remove_user': remove_user
            }
        )

    @classmethod
    async def run(cls, ws_response: WSResponse, meta: Meta, command: str = None, message_json: Dict[str, str] = None):
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
                notification=RemoveUserAction.get_remove_user_notification(user_name=meta.user_name, room_name=room_name, remove_user=remove_user, success=True, reason='')
            )

            return meta

        except:
            await NotificationStore().process(
                ws=ws_response,
                notification=RemoveUserAction.get_remove_user_notification(user_name=meta.user_name, room_name=room_name, remove_user=remove_user, success=False, reason=NOT_ALLOWED)
            )
        
        return meta

class OpenDialogueAction(Command):
    
    @staticmethod
    def get_open_dialogue_notification(user_name: str, with_user: str, success: bool, reason: str):
        return UserAction(
            action=CommandType.open_dialogue,
            datetime=str(datetime.now()),
            expired=False,
            success=success,
            reason=reason,
            user_name=user_name,
            payload={
                'with_user': with_user
            }
        )
    
    @classmethod
    async def run(cls, ws_response: WSResponse, meta: Meta, command: str = None, message_json: Dict[str, str] = None):

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
                    key=None,
                    name='',
                    room_type=RoomType.private,
                    admins=[meta.user_name, with_user],
                    allowed=[meta.user_name, with_user],
                    deleted=False
                )
            )

            await NotificationStore().process(
                ws=ws_response,
                notification=OpenDialogueAction.get_open_dialogue_notification(user_name=meta.user_name, with_user=with_user, success=True, reason='')
            )
        
        except DialogueOpenedAlready:
            await NotificationStore().process(
                ws=ws_response,
                notification=OpenDialogueAction.get_open_dialogue_notification(user_name=meta.user_name, with_user=with_user, success=False, reason=DIALOGUE_OPENED_ERR)
            )
        except NotAuthorized:
            await NotificationStore().process(
                ws=ws_response,
                notification=OpenDialogueAction.get_open_dialogue_notification(user_name=meta.user_name, with_user=with_user, success=False, reason=NO_AUTH)
            )
        
        return meta

class DeleteDialogueAction(Command):

    @staticmethod
    def get_open_dialogue_notification(user_name: str, with_user: str, success: bool, reason: str):
        return UserAction(
            action=CommandType.delete_dialogue,
            datetime=str(datetime.now()),
            expired=False,
            success=success,
            reason=reason,
            user_name=user_name,
            payload={
                'with_user': with_user
            }
        )

    @classmethod
    async def run(cls, ws_response: WSResponse, meta: Meta, command: str = None, message_json: Dict[str, str] = None):
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
                notification=DeleteDialogueAction.get_open_dialogue_notification(user_name=meta.user_name, with_user=with_user, success=True, reason='')
            )

        except NoRoomFound:
            await NotificationStore().process(
                ws=ws_response,
                notification=DeleteDialogueAction.get_open_dialogue_notification(user_name=meta.user_name, with_user=with_user, success=False, reason=NO_DIALOGUE)
            )

        return meta