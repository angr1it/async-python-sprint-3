from pydantic import BaseModel
from typing import Optional

from chat.command_types import CommandType
from chat.subjects import Subjects
from chat.server.state.room import RoomType


class SendModel(BaseModel):
    command: CommandType = CommandType.send
    message: str
    room: Optional[str] = ""
    private: Optional[bool] = False
    to_user: Optional[str] = Subjects.all


class HistoryModel(BaseModel):
    command: CommandType = CommandType.history
    room: Optional[str] = ""
    notification_count: Optional[int] = 20


class CreateRoomModel(BaseModel):
    command: CommandType = CommandType.create_room
    room_name: str
    room_type: RoomType


class JoinRoomModel(BaseModel):
    command: CommandType = CommandType.join_room
    room_name: str


class AddUserModel(BaseModel):
    command: CommandType = CommandType.add_user
    room_name: str
    new_user: str


class RemoveUserModel(BaseModel):
    command: CommandType = CommandType.remove_user
    room_name: str
    remove_user: str


class LeaveRoomModel(BaseModel):
    command: CommandType = CommandType.leave_room
    room_name: str


class RegisterModel(BaseModel):
    command: CommandType = CommandType.register
    username: str
    password: str


class LoginModel(BaseModel):
    command: CommandType = CommandType.login
    username: str
    password: str


class LogoutModel(BaseModel):
    command: CommandType = CommandType.logout


class DeleteRoomModel(BaseModel):
    command: CommandType = CommandType.delete_room
    room_name: str


class OpenDialogueModel(BaseModel):
    command: CommandType = CommandType.open_dialogue
    with_user: str


class DeleteDialogueModel(BaseModel):
    command: CommandType = CommandType.delete_dialogue
    with_user: str


class PublishFileModel(BaseModel):
    command: CommandType = CommandType.publish_file
    filename: str


class LoadFileModel(BaseModel):
    command: CommandType = CommandType.load_file
    key: str
