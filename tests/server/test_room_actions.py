import aiounittest
from aiohttp.test_utils import make_mocked_coro
from unittest.mock import MagicMock
import uuid
from freezegun import freeze_time

from chat.server.state.user import (
    UserStore
)
from chat.server.room_actions import (
    CreateRoom,
    AddUser,
    JoinRoom,
    RemoveUser,
    LeaveRoom
)
from chat.server.state.room import (
    RoomStore
)
from chat.command_types import CommandType
from chat.server.state.meta import Meta
from chat.server.state.user import User
from chat.requests_examples import (
    test_dt_str,
    CreateOpenRoomRequests,
    JoinOpenRequests,
    RestrictedRoomRequests,

)
from chat.singleton import singleton
from chat.exceptions import (
    UnknownError,
    NoRegistredUserFound
)

class TestServerActions(aiounittest.AsyncTestCase):

    def setUp(self) -> None:
        
        self.mock_ws = MagicMock()
        self.mock_ws.send_json = make_mocked_coro()

        self.meta_anon = Meta(key=uuid.uuid4(), user_name='anonymus_12314', loggedin=False)

        self.user1 = UserStore().register(username='user1', password='123')
        self.user2 = UserStore().register(username='user2', password='123')

        self.meta_user1 = Meta(key=uuid.uuid4(), user_name=self.user1.username, loggedin=True)
        self.meta_user2 = Meta(key=uuid.uuid4(), user_name=self.user2.username, loggedin=True)

    def tearDown(self) -> None:
        singleton.instances = {}

    @freeze_time(test_dt_str)
    async def test_open_room(self):

        await CreateRoom().run(
            ws_response=self.mock_ws,
            meta=self.meta_anon,
            command=CommandType.create_room,
            message_json=CreateOpenRoomRequests.JSON_REQ.value
        )
        self.assertIsNone(self.mock_ws.send_json.assert_called_with(CreateOpenRoomRequests.JSON_RESP_ANON.value))

        await CreateRoom().run(
            ws_response=self.mock_ws,
            meta=self.meta_user1,
            command=CommandType.create_room,
            message_json=CreateOpenRoomRequests.JSON_REQ.value
        )
        self.assertIsNone(self.mock_ws.send_json.assert_called_with(CreateOpenRoomRequests.JSON_RESP_SUCCESS.value))

        with self.assertRaises(NoRegistredUserFound):
            await JoinRoom().run(
                ws_response=self.mock_ws,
                meta=self.meta_anon,
                command=CommandType.join_room,
                message_json=JoinOpenRequests.REQ.value,
            )

        await JoinRoom().run(
            ws_response=self.mock_ws,
            meta=self.meta_user2,
            command=CommandType.join_room,
            message_json=JoinOpenRequests.REQ.value,
        )
        self.assertIsNone(self.mock_ws.send_json.assert_called_with(JoinOpenRequests.RESP_SUCESS.value))

    @freeze_time(test_dt_str)
    async def test_restricted_room(self):

        await CreateRoom().run(
            ws_response=self.mock_ws,
            meta=self.meta_user1,
            command=CommandType.create_room,
            message_json=RestrictedRoomRequests.CREATE_ROOM_REQ.value
        )
        self.assertIsNone(self.mock_ws.send_json.assert_called_with(RestrictedRoomRequests.CREATE_ROOM_RESP_SUCCESS.value))

        await AddUser().run(
            ws_response=self.mock_ws,
            meta=self.meta_user2,
            command=CommandType.add_user,
            message_json=RestrictedRoomRequests.ADD_USER_REQ.value
        )
        self.assertIsNone(self.mock_ws.send_json.assert_called_with(RestrictedRoomRequests.ADD_USER_RESP_NOT_ALLOWED.value))

        await AddUser().run(
            ws_response=self.mock_ws,
            meta=self.meta_anon,
            command=CommandType.add_user,
            message_json=RestrictedRoomRequests.ADD_USER_REQ.value
        )
        self.assertIsNone(self.mock_ws.send_json.assert_called_with(RestrictedRoomRequests.ADD_USER_RESP_NO_AUTH.value))

        await AddUser().run(
            ws_response=self.mock_ws,
            meta=self.meta_user1,
            command=CommandType.add_user,
            message_json=RestrictedRoomRequests.ADD_USER_REQ.value
        )
        self.assertIsNone(self.mock_ws.send_json.assert_called_with(RestrictedRoomRequests.ADD_USER_RESP_SUCCESS.value))
        self.assertFalse(RoomStore().user_in_room(user=self.user2, room=RoomStore().get_room_by_name(RestrictedRoomRequests.CREATE_ROOM_REQ.value['room_name'])))

        with self.assertRaises(NoRegistredUserFound):
            await JoinRoom().run(
                ws_response=self.mock_ws,
                meta=self.meta_anon,
                command=CommandType.join_room,
                message_json=RestrictedRoomRequests.JOIN_REQ.value
            )

        await JoinRoom().run(
            ws_response=self.mock_ws,
            meta=self.meta_user2,
            command=CommandType.join_room,
            message_json=RestrictedRoomRequests.JOIN_REQ.value
        )
        self.assertIsNone(self.mock_ws.send_json.assert_called_with(RestrictedRoomRequests.JOIN_RESP_SUCCESS.value))
        self.assertTrue(RoomStore().user_in_room(user=self.user2, room=RoomStore().get_room_by_name(RestrictedRoomRequests.CREATE_ROOM_REQ.value['room_name'])))

        await RemoveUser().run(
            ws_response=self.mock_ws,
            meta=self.meta_anon,
            command=CommandType.remove_user,
            message_json=RestrictedRoomRequests.REMOVE_USER_REQ.value
        )
        self.assertIsNone(self.mock_ws.send_json.assert_called_with(RestrictedRoomRequests.REMOVE_USER_RESP_ANON.value))

        await RemoveUser().run(
            ws_response=self.mock_ws,
            meta=self.meta_user1,
            command=CommandType.remove_user,
            message_json=RestrictedRoomRequests.REMOVE_USER_REQ.value
        )
        self.assertIsNone(self.mock_ws.send_json.assert_called_with(RestrictedRoomRequests.REMOVE_USER_RESP_SUCCESS.value))
        self.assertFalse(RoomStore().user_in_room(user=self.user2, room=RoomStore().get_room_by_name(RestrictedRoomRequests.CREATE_ROOM_REQ.value['room_name'])))

        with self.assertRaises(NoRegistredUserFound):
            await LeaveRoom().run(
                ws_response=self.mock_ws,
                meta=self.meta_anon,
                command=CommandType.leave_room,
                message_json=RestrictedRoomRequests.LEAVE_REQ.value
            )

        await LeaveRoom().run(
            ws_response=self.mock_ws,
            meta=self.meta_user1,
            command=CommandType.leave_room,
            message_json=RestrictedRoomRequests.LEAVE_REQ.value
        )
        self.assertFalse(RoomStore().user_in_room(user=self.user1, room=RoomStore().get_room_by_name(RestrictedRoomRequests.LEAVE_ROOM_SUCCESS.value['room_name'])))



          