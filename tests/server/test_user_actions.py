import aiounittest
from aiohttp.test_utils import make_mocked_coro
from unittest.mock import MagicMock
import uuid
from freezegun import freeze_time

from chat.server.state.user import (
    UserStore
)
from chat.server.user_actions import (
    Register,
    Login,
    Logout
)

from chat.command_types import CommandType
from chat.server.state.meta import Meta
from chat.server.state.user import User
from chat.requests_examples import (
    test_dt_str,
    RegisterRequests,
    LoginRequests,
    LogoutRequests
)
from chat.singleton import singleton

class TestServerActions(aiounittest.AsyncTestCase):

    def setUp(self) -> None:
        
        self.mock_ws = MagicMock()
        self.mock_ws.send_json = make_mocked_coro()

        self.meta = Meta(key=uuid.uuid4(), user_name='anonymus_12314', loggedin=False)
    
    def tearDown(self) -> None:
        singleton.instances = {}

    @freeze_time(test_dt_str)
    async def test_register(self):

        await Register().run(
            ws_response=self.mock_ws,
            meta = self.meta,
            command=CommandType.register,
            message_json=RegisterRequests.REGISTER_JSON_REQ.value
        )
        self.assertEqual(UserStore().get_user(RegisterRequests.REGISTER_JSON_REQ.value['username']).username, RegisterRequests.REGISTER_JSON_REQ.value['username'])
        self.assertIsNone(self.mock_ws.send_json.assert_called_with(RegisterRequests.REGISTER_JSON_RESP.value))

    @freeze_time(test_dt_str)
    async def test_login_logout(self):

        await Register().run(
            ws_response=self.mock_ws,
            meta = self.meta,
            command=CommandType.register,
            message_json=RegisterRequests.REGISTER_JSON_REQ.value
        )

        await Login().run(
            ws_response=self.mock_ws,
            meta = self.meta,
            command=CommandType.login,
            message_json=LoginRequests.LOGIN_JSON_REQ_BAD.value
        )

        self.assertFalse(self.meta.loggedin)
        self.assertIsNone(self.mock_ws.send_json.assert_called_with(LoginRequests.LOGIN_JSON_RESP_BAD.value))

        await Login().run(
            ws_response=self.mock_ws,
            meta = self.meta,
            command=CommandType.login,
            message_json=LoginRequests.LOGIN_JSON_REQ.value
        )

        self.assertTrue(self.meta.loggedin)
        self.assertEqual(LoginRequests.LOGIN_JSON_REQ.value['username'], self.meta.user_name)
        self.assertIsNone(self.mock_ws.send_json.assert_called_with(LoginRequests.LOGIN_JSON_RESP.value))

        await Login().run(
            ws_response=self.mock_ws,
            meta = self.meta,
            command=CommandType.login,
            message_json=LoginRequests.LOGIN_JSON_REQ.value
        )

        self.assertTrue(self.meta.loggedin)
        self.assertEqual(LoginRequests.LOGIN_JSON_REQ.value['username'], self.meta.user_name)
        self.assertIsNone(self.mock_ws.send_json.assert_called_with(LoginRequests.LOGIN_JSON_RESP_AGAIN.value))


        await Logout().run(
            ws_response=self.mock_ws,
            meta = self.meta,
            command=CommandType.logout,
            message_json=LogoutRequests.LOGOUT_JSON_REQ.value
        )

        self.assertFalse(self.meta.loggedin)
        self.assertNotEqual(LoginRequests.LOGIN_JSON_REQ.value['username'], self.meta.user_name)




