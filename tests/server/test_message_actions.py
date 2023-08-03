import aiounittest
from asyncmock import AsyncMock
from aiohttp.test_utils import make_mocked_coro, make_mocked_request
from unittest.mock import MagicMock, patch
import uuid
from freezegun import freeze_time

from chat.server.state.user import (
    User,
    UserStore
)
from chat.server.message_actions import (
    Send,
    History,

)
from chat.command_types import CommandType
from chat.server.state.meta import Meta
from chat.server.state.user import User
from chat.requests_examples import (
    test_dt_str,
    SendRequests,
    HistoryRequests

)
from chat.singleton import singleton

class TestServerActions(aiounittest.AsyncTestCase):

    def setUp(self) -> None:
        
        self.mock_ws = MagicMock()
        self.mock_ws.send_json = make_mocked_coro()

        user = UserStore().register(username='andre', password='123')
        self.meta = Meta(key=uuid.uuid4(), user_name=user.username, loggedin=True)

    
    def tearDown(self) -> None:
        singleton.instances = {}
    
    @freeze_time(test_dt_str)
    async def test_send(self):

        await Send().run(
            ws_response=self.mock_ws,
            meta=self.meta,
            command=CommandType.send,
            message_json=SendRequests.SEND_JSON_REQ.value
        )

        self.assertIsNone(self.mock_ws.send_json.assert_called_with(SendRequests.SEND_JSON_RESP.value))

    @freeze_time(test_dt_str)
    async def test_history(self):

        await Send().run(
            ws_response=self.mock_ws,
            meta=self.meta,
            command=CommandType.send,
            message_json=SendRequests.SEND_JSON_REQ.value
        )

        await History().run(
            ws_response=self.mock_ws,
            meta=self.meta,
            command=CommandType.history,
            message_json=HistoryRequests.HISTORY_JSON_REQ.value
        )

        self.assertIsNone(self.mock_ws.send_json.assert_called_with(HistoryRequests.HISTORY_JSON_RESP.value))
