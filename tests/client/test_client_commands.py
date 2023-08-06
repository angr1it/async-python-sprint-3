import aiounittest
from unittest.mock import MagicMock

from chat.utils.async_mock import AsyncMock
from chat.client.client_commands import (
    SendCommand,
    HistoryCommand,
    CreateRoomCommand,
    JoinRoomCommand,
    AddUserCommand,
    RemoveUserCommand,
    LeaveRoomCommand,
    RegisterCommand,
    LoginCommand,
    LogoutCommand,
    OpenDialogueCommand,
    DeleteRoomCommand,
    DeleteDialogueCommand,
    SendPrivateCommand
)

from chat.command_types import CommandType
from chat.requests_examples import (
    SendRequests,
    HistoryRequests,
    CreateOpenRoomRequests,
    JoinOpenRequests,
    RestrictedRoomRequests,
    RegisterRequests,
    LoginRequests,
    LogoutRequests,
    OpenDialogueRequests
)


class TestClientCommands(aiounittest.AsyncTestCase):

    def setUp(self) -> None:

        self.mock_ws = MagicMock()
        self.mock_ws.send_json = AsyncMock()

    async def test_send(self):

        await SendCommand().run(
            ws=self.mock_ws,
            command=CommandType.send,
            content=SendRequests.SEND_COMMAND.value
        )
        self.assertIsNone(self.mock_ws.send_json.assert_called_with(
            SendRequests.SEND_JSON_REQ.value
        ))

        await SendPrivateCommand().run(
            ws=self.mock_ws,
            command=CommandType.send_private,
            content=SendRequests.SEND_PRIVATE_COMMAND.value
        )

        self.assertIsNone(self.mock_ws.send_json.assert_called_with(
            SendRequests.SEND_PRIVATE_JSON_REQ.value
        ))

    async def test_history(self):

        await HistoryCommand().run(
            ws=self.mock_ws,
            command=CommandType.history,
            content=HistoryRequests.COMMAND.value
        )

        self.assertIsNone(self.mock_ws.send_json.assert_called_with(
            HistoryRequests.JSON_REQ.value
        ))

        await HistoryCommand().run(
            ws=self.mock_ws,
            command=CommandType.history,
            content=HistoryRequests.USER_COMMAND.value
        )

        self.assertIsNone(self.mock_ws.send_json.assert_called_with(
            HistoryRequests.USER_JSON_REQ.value
        ))

        await HistoryCommand().run(
            ws=self.mock_ws,
            command=CommandType.history,
            content=HistoryRequests.USER_DEFAULT_COMMAND.value
        )

        self.assertIsNone(self.mock_ws.send_json.assert_called_with(
            HistoryRequests.USER_DEFAULT_JSON_REQ.value
        ))

    async def test_create_room(self):

        await CreateRoomCommand().run(
            ws=self.mock_ws,
            command=CommandType.create_room,
            content=CreateOpenRoomRequests.CREATE_COMMAND.value
        )

        self.assertIsNone(self.mock_ws.send_json.assert_called_with(
            CreateOpenRoomRequests.CREATE_JSON_REQ.value
        ))

    async def test_join_room(self):

        await JoinRoomCommand().run(
            ws=self.mock_ws,
            command=CommandType.join_room,
            content=JoinOpenRequests.COMMAND.value
        )

        self.assertIsNone(self.mock_ws.send_json.assert_called_with(
            JoinOpenRequests.REQ.value
        ))

    async def test_add_user(self):

        await AddUserCommand().run(
            ws=self.mock_ws,
            command=CommandType.add_user,
            content=RestrictedRoomRequests.ADD_USER_COMMAND.value
        )

        self.assertIsNone(self.mock_ws.send_json.assert_called_with(
            RestrictedRoomRequests.ADD_USER_REQ.value
        ))

    async def test_remove_user(self):

        await RemoveUserCommand().run(
            ws=self.mock_ws,
            command=CommandType.remove_user,
            content=RestrictedRoomRequests.REMOVE_USER_COMMAND.value
        )

        self.assertIsNone(self.mock_ws.send_json.assert_called_with(
            RestrictedRoomRequests.REMOVE_USER_REQ.value
        ))

    async def test_leave_room(self):

        await LeaveRoomCommand().run(
            ws=self.mock_ws,
            command=CommandType.leave_room,
            content=RestrictedRoomRequests.LEAVE_COMMAND.value
        )

        self.assertIsNone(self.mock_ws.send_json.assert_called_with(
            RestrictedRoomRequests.LEAVE_REQ.value
        ))

    async def test_register(self):

        await RegisterCommand().run(
            ws=self.mock_ws,
            command=CommandType.register,
            content=RegisterRequests.COMMAND.value
        )

        self.assertIsNone(self.mock_ws.send_json.assert_called_with(
            RegisterRequests.JSON_REQ.value
        ))

    async def test_login(self):

        await LoginCommand().run(
            ws=self.mock_ws,
            command=CommandType.login,
            content=LoginRequests.COMMAND.value
        )

        self.assertIsNone(self.mock_ws.send_json.assert_called_with(
            LoginRequests.JSON_REQ.value
        ))

    async def test_logout(self):

        await LogoutCommand().run(
            ws=self.mock_ws,
            command=CommandType.logout,
            content=LogoutRequests.LOGOUT_COMMAND.value
        )

        self.assertIsNone(self.mock_ws.send_json.assert_called_with(
            LogoutRequests.LOGOUT_JSON_REQ.value
        ))

    async def test_open_dialogue(self):

        await OpenDialogueCommand().run(
            ws=self.mock_ws,
            command=CommandType.open_dialogue,
            content=OpenDialogueRequests.OPEN_COMMAND.value
        )

        self.assertIsNone(self.mock_ws.send_json.assert_called_with(
            OpenDialogueRequests.OPEN_JSON_REQ.value
        ))

    async def test_delete_dialogue(self):

        await DeleteDialogueCommand().run(
            ws=self.mock_ws,
            command=CommandType.delete_dialogue,
            content=OpenDialogueRequests.DELETE_COMMAND.value

        )

        self.assertIsNone(self.mock_ws.send_json.assert_called_with(
            OpenDialogueRequests.DELETE_JSON_REQ.value
        ))

    async def test_delete_room(self):

        await DeleteRoomCommand().run(
            ws=self.mock_ws,
            command=CommandType.delete_room,
            content=CreateOpenRoomRequests.DELETE_COMMAND.value
        )

        self.assertIsNone(self.mock_ws.send_json.assert_called_with(
            CreateOpenRoomRequests.DELETE_JSON_REQ.value
        ))
