from chat.command_types import CommandType
from chat.server.command import Command
from chat.server.message_actions import (
    SendAction,
    HistoryAction
)
from chat.server.user_actions import (
    LoginAction,
    LogoutAction,
    RegisterAction,
    QuitAction
)
from chat.server.room_actions import (
    OpenDialogueAction,
    CreateRoomAction,
    DeleteRoomAction,
    JoinRoomAction,
    LeaveRoomAction,
    AddUserAction,
    RemoveUserAction,
    DeleteDialogueAction
)
from .file_actions import (
    PublishFileAction,
    LoadFileAction
)


def init_commands() -> dict[CommandType, type[Command]]:
    commands: dict[CommandType, type[Command]] = {}

    commands[CommandType.send] = SendAction
    commands[CommandType.history] = HistoryAction

    commands[CommandType.login] = LoginAction
    commands[CommandType.logout] = LogoutAction
    commands[CommandType.register] = RegisterAction

    commands[CommandType.open_dialogue] = OpenDialogueAction
    commands[CommandType.delete_dialogue] = DeleteDialogueAction
    commands[CommandType.create_room] = CreateRoomAction
    commands[CommandType.delete_room] = DeleteRoomAction
    commands[CommandType.join_room] = JoinRoomAction
    commands[CommandType.leave_room] = LeaveRoomAction
    commands[CommandType.add_user] = AddUserAction
    commands[CommandType.remove_user] = RemoveUserAction

    commands[CommandType.load_file] = LoadFileAction
    commands[CommandType.publish_file] = PublishFileAction

    commands[CommandType.quit] = QuitAction

    return commands
