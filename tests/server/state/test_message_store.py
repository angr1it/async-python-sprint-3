import aiounittest
from unittest.mock import MagicMock
from datetime import datetime
from freezegun import freeze_time

from chat.server.state.room import (
    Room,
    RoomStore,
    RoomType
)
from chat.utils.async_mock import AsyncMock
from chat.server.state.user import (
    User,
    UserStore
)

from chat.server.state.message import (
    NotificationStore,
    get_message_notification
)
from chat.server.message_actions import SendAction

from chat.singleton import singleton
from chat.command_types import CommandType

from chat.requests_examples import (
    test_dt_str
)

from chat.utils.my_response import WSResponse
class TestMessageStore(aiounittest.AsyncTestCase):

    def setUp(self) -> None:
                
        self.ws_response = MagicMock()
        self.ws_response.send_json = AsyncMock()
        
    def tearDown(self) -> None:

        singleton.instances = {}

    @freeze_time(test_dt_str)
    async def test_store(self):

        user = UserStore().register(username='user', password='123')

        room = RoomStore().add_room(Room(
            key=None,
            name='room',
            room_type=RoomType.open,
            admins=[user.username],
            allowed=[user.username],
            deleted=False
        ))

        await NotificationStore().process(
            ws=self.ws_response,
            notification=get_message_notification(room_name=room.name, user_name=user.username, success=True, reason='',private=False, to='', message='Hello, world!')
        )

        await NotificationStore().process(
            ws=self.ws_response,
            notification=get_message_notification(room_name=room.name, user_name=user.username, success=True, reason='',private=False, to='', message='Hello, hello!')
        )

        data = NotificationStore().get_n_messages(room=room, n=1)
        self.assertEqual(len(data), 1)
        self.assertDictEqual(
            data[0],
            {
                'action':  CommandType.send,
                'success': True,
                'reason': '',
                'datetime': str(datetime.now()),
                'user': 'user',
                'room_name': 'room',
                'payload': {
                    'private': False,
                    'to': '',
                    'message': 'Hello, world!'
                }
            }
        )