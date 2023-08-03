import aiounittest
from asyncmock import AsyncMock

import unittest
from unittest.mock import patch, MagicMock
from aiohttp import web
from datetime import datetime
import dataclasses

from chat.server.state.room import (
    Room,
    RoomStore,
    RoomType
)

from chat.server.state.user import (
    User,
    UserStore
)

from chat.server.state.message import (
    Message,
    NotificationStore
)

from chat.singleton import singleton
from chat.command_types import CommandType

class TestMessageStore(aiounittest.AsyncTestCase):

    def tearDown(self) -> None:
        singleton.instances = {}

    @patch('aiohttp.web.WebSocketResponse', new_callable=AsyncMock(web.WebSocketResponse))
    async def test_store(self, ws_response):

        user = UserStore().register(username='user', password='123')

        room = RoomStore().add_room(Room(
            key=None,
            name='room',
            room_type=RoomType.open,
            admins=[user.username],
            allowed=[user.username],
            deleted=False
        ))

        dt = datetime.now()
        await NotificationStore().process(
            ws=ws_response,
            notification=Message(
                action=CommandType.send,
                datetime=dt,
                expired=False,
                success=True,
                reason='',
                room_name=room.name,
                user_name=user.username,
                to='',
                private=False,
                message_str='Hello, world!'
            )
        )

        await NotificationStore().process(
            ws=ws_response,
            notification=Message(
                action=CommandType.send,
                datetime=dt,
                expired=False,
                success=True,
                reason='',
                room_name=room.name,
                user_name=user.username,
                to='',
                private=False,
                message_str='Hello, hello!'
            )
        )

        data = NotificationStore().get_n_messages(room=room, n=1)
        self.assertEqual(len(data), 1)
        self.assertDictEqual(
            data[0],
            {
                'action':  CommandType.send,
                'datetime': str(dt),
                'private': False,
                'room': 'room',
                'from': 'user',
                'to': '',
                'message': 'Hello, world!'
            }
        )