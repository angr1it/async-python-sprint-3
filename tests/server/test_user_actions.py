import aiounittest
from unittest.mock import MagicMock
import uuid


from freezegun import freeze_time
from mock import patch
import argon2

from chat.server.state.user import UserStore
from chat.server.user_actions import RegisterAction, LoginAction, LogoutAction
from chat.command_types import CommandType
from chat.server.state.meta import Meta
from chat.requests_examples import (
    test_dt_str,
    RegisterRequests,
    LoginRequests,
    LogoutRequests,
)
from chat.singleton import singleton


class AsyncMock(MagicMock):
    async def __call__(self, *args, **kwargs):
        return super(AsyncMock, self).__call__(*args, **kwargs)


class TestServerActions(aiounittest.AsyncTestCase):
    def setUp(self) -> None:
        self.mock_ws = MagicMock()
        self.mock_ws.send_json = AsyncMock()

        self.meta = Meta(
            key=uuid.uuid4(),
            user_name="anonymus_12314",
            loggedin=False
        )

    def tearDown(self) -> None:
        singleton.instances = {}

    @freeze_time(test_dt_str)
    async def test_register(self):
        await RegisterAction().run(
            ws_response=self.mock_ws,
            meta=self.meta,
            command=CommandType.register,
            message_json=RegisterRequests.JSON_REQ.value,
        )
        self.assertEqual(
            UserStore().get_user(
                RegisterRequests.JSON_REQ.value["username"]
            ).username,
            RegisterRequests.JSON_REQ.value["username"],
        )
        self.assertIsNone(self.mock_ws.send_json.assert_called_with(
            RegisterRequests.JSON_RESP.value
        ))

    @freeze_time(test_dt_str)
    @patch('argon2.verify_password')
    async def test_login_logout(self, verify_password):
        
        await RegisterAction().run(
            ws_response=self.mock_ws,
            meta=self.meta,
            command=CommandType.register,
            message_json=RegisterRequests.JSON_REQ.value,
        )

        verify_password.return_value = False # noqa: F841
        await LoginAction().run(
            ws_response=self.mock_ws,
            meta=self.meta,
            command=CommandType.login,
            message_json=LoginRequests.JSON_REQ_BAD.value,
        )

        self.assertFalse(self.meta.loggedin)
        self.assertIsNone(
            self.mock_ws.send_json.assert_called_with(
                LoginRequests.LOGIN_JSON_RESP_BAD.value
            )
        )

        verify_password.return_value = True # noqa: F841
        await LoginAction().run(
            ws_response=self.mock_ws,
            meta=self.meta,
            command=CommandType.login,
            message_json=LoginRequests.JSON_REQ.value,
        )

        self.assertTrue(self.meta.loggedin)
        self.assertEqual(
            LoginRequests.JSON_REQ.value["username"],
            self.meta.user_name
        )
        self.assertIsNone(self.mock_ws.send_json.assert_called_with(
            LoginRequests.JSON_RESP.value
        ))

        verify_password.return_value = True # noqa: F841
        await LoginAction().run(
            ws_response=self.mock_ws,
            meta=self.meta,
            command=CommandType.login,
            message_json=LoginRequests.JSON_REQ.value,
        )

        self.assertTrue(self.meta.loggedin)
        self.assertEqual(
            LoginRequests.JSON_REQ.value["username"],
            self.meta.user_name
        )
        self.assertIsNone(
            self.mock_ws.send_json.assert_called_with(
                LoginRequests.LOGIN_JSON_RESP_AGAIN.value
            )
        )

        await LogoutAction().run(
            ws_response=self.mock_ws,
            meta=self.meta,
            command=CommandType.logout,
            message_json=LogoutRequests.LOGOUT_JSON_REQ.value,
        )

        self.assertFalse(self.meta.loggedin)
        self.assertNotEqual(
            LoginRequests.JSON_REQ.value["username"], self.meta.user_name
        )
