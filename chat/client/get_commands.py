from typing import Dict

from .client_commands import (
    Command,
    SendCommand,
    HistoryCommand,
    LoginCommand,
    LogoutCommand,
    RegisterCommand,
    OpenDialogueCommand,
    CreateRoomCommand,
    DeleteRoomCommand,
    JoinRoomCommand,
    LeaveRoomCommand,
    AddUserCommand,
    RemoveUserCommand,
    LoadFileCommand,
    PublishFileCommand,
    DeleteDialogueCommand,
    SendPrivateCommand
)
from ..command_types import CommandType

def init_commands() -> Dict[CommandType, Command]:
    commands: Dict[Command] = {}


    commands[CommandType.send] = SendCommand
    commands[CommandType.send_private] = SendPrivateCommand
    commands[CommandType.history] = HistoryCommand

    commands[CommandType.login] = LoginCommand
    commands[CommandType.logout] = LogoutCommand
    commands[CommandType.register] = RegisterCommand

    commands[CommandType.open_dialogue] = OpenDialogueCommand
    commands[CommandType.delete_dialogue] = DeleteDialogueCommand
    commands[CommandType.create_room] = CreateRoomCommand
    commands[CommandType.delete_room] = DeleteRoomCommand
    commands[CommandType.join_room] = JoinRoomCommand
    commands[CommandType.leave_room] = LeaveRoomCommand
    commands[CommandType.add_user] = AddUserCommand
    commands[CommandType.remove_user] = RemoveUserCommand

    commands[CommandType.load_file] = LoadFileCommand
    commands[CommandType.publish_file] = PublishFileCommand

    return commands