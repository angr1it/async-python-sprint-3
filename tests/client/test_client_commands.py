import aiounittest
from asyncmock import AsyncMock
from aiohttp.test_utils import make_mocked_coro, make_mocked_request

import unittest
from unittest.mock import patch, MagicMock
from aiohttp import ClientWebSocketResponse
from datetime import datetime
import dataclasses


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
    LogoutCommand
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
    LogoutRequests
)
class TestClientCommands(aiounittest.AsyncTestCase):

    def setUp(self) -> None:
        
        self.mock_ws = MagicMock()
        self.mock_ws.send_json = make_mocked_coro()
    
    async def test_send(self):
        
        await SendCommand().run(
            websocket=self.mock_ws,
            command=CommandType.send,
            content=SendRequests.SEND_COMMAND.value
        )

        self.assertIsNone(self.mock_ws.send_json.assert_called_with(SendRequests.SEND_JSON_REQ.value))

    async def test_history(self):

        await HistoryCommand().run(
            websocket=self.mock_ws,
            command=CommandType.history,
            content=HistoryRequests.HISTORY_COMMAND.value
        )

        self.assertIsNone(self.mock_ws.send_json.assert_called_with(HistoryRequests.HISTORY_JSON_REQ.value))

    async def test_create_room(self):

        await CreateRoomCommand().run(
            websocket=self.mock_ws,
            command=CommandType.create_room,
            content=CreateOpenRoomRequests.COMMAND.value
        )

        self.assertIsNone(self.mock_ws.send_json.assert_called_with(CreateOpenRoomRequests.JSON_REQ.value))

    async def test_join_room(self):

        await JoinRoomCommand().run(
            websocket=self.mock_ws,
            command=CommandType.join_room,
            content=JoinOpenRequests.COMMAND.value
        )

        self.assertIsNone(self.mock_ws.send_json.assert_called_with(JoinOpenRequests.REQ.value))

    async def test_add_user(self):

        await AddUserCommand().run(
            websocket=self.mock_ws,
            command=CommandType.add_user,
            content=RestrictedRoomRequests.ADD_USER_COMMAND.value
        )

        self.assertIsNone(self.mock_ws.send_json.assert_called_with(RestrictedRoomRequests.ADD_USER_REQ.value))

    async def test_remove_user(self):

        await RemoveUserCommand().run(
            websocket=self.mock_ws,
            command=CommandType.remove_user,
            content=RestrictedRoomRequests.REMOVE_USER_COMMAND.value
        )

        self.assertIsNone(self.mock_ws.send_json.assert_called_with(RestrictedRoomRequests.REMOVE_USER_REQ.value))

    async def test_leave_room(self):

        await LeaveRoomCommand().run(
            websocket=self.mock_ws,
            command=CommandType.leave_room,
            content=RestrictedRoomRequests.LEAVE_COMMAND.value
        )

        self.assertIsNone(self.mock_ws.send_json.assert_called_with(RestrictedRoomRequests.LEAVE_REQ.value))

    async def test_register(self):

        await RegisterCommand().run(
            websocket=self.mock_ws,
            command=CommandType.register,
            content=RegisterRequests.REGISTER_COMMAND.value
        )

        self.assertIsNone(self.mock_ws.send_json.assert_called_with(RegisterRequests.REGISTER_JSON_REQ.value))

    async def test_login(self):

        await LoginCommand().run(
            websocket=self.mock_ws,
            command=CommandType.login,
            content=LoginRequests.LOGIN_COMMAND.value
        )

        self.assertIsNone(self.mock_ws.send_json.assert_called_with(LoginRequests.LOGIN_JSON_REQ.value))

    async def test_logout(self):

        await LogoutCommand().run(
            websocket=self.mock_ws,
            command=CommandType.logout,
            content=LogoutRequests.LOGOUT_COMMAND.value
        )

        self.assertIsNone(self.mock_ws.send_json.assert_called_with(LogoutRequests.LOGOUT_JSON_REQ.value))