import unittest
from datetime import datetime

from chat.server.state.room import (
    Room,
    RoomType
)
from chat.server.state.user import User

from chat.server.state.message import (
    Message,
    ConnectAnon
)
from chat.command_types import CommandType

class TestMessageStore(unittest.TestCase):

    def test_message(self):
        
        user = User(username='user', password='123')

        room = Room(
            key=None,
            name='room',
            room_type=RoomType.open,
            admins=[user.username],
            allowed=[user.username],
            deleted=False
        )

        dt = datetime.now()

        notification = Message(
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

        self.assertDictEqual(
            notification.get_notification(),
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

    def test_connect_anon(self):
        
        dt = datetime.now()

        notification = ConnectAnon(
            action=CommandType.connected,
            datetime=dt,
            expired=False,
            success=True,
            reason='',
            name='anon',
        )

        self.assertDictEqual(
            notification.get_notification(),
            {
                'action':  CommandType.connected,
                'datetime': str(dt),
                'success': True,
                'reason': '', 
                'name': 'anon'
            }
        )
    