import unittest
from datetime import datetime
from freezegun import freeze_time

from chat.server.state.room import Room, RoomType
from chat.server.state.user import User

from chat.server.state.message import get_message_notification
from chat.command_types import CommandType
from chat.requests_examples import test_dt_str
from chat.server.state.message import get_connected_notification


class TestMessageStore(unittest.TestCase):
    @freeze_time(test_dt_str)
    def test_message(self):
        user = User(username="user", password="123")

        room = Room(
            key=None,
            name="room",
            room_type=RoomType.open,
            admins=[user.username],
            allowed=[user.username],
            deleted=False,
        )

        notification = get_message_notification(
            room_name=room.name,
            user_name=user.username,
            success=True,
            reason="",
            private=False,
            to="",
            message="Hello, world!",
        )

        self.assertDictEqual(
            notification.get_notification(),
            {
                "action": CommandType.send,
                "success": True,
                "reason": "",
                "datetime": str(datetime.now()),
                "user": "user",
                "room_name": "room",
                "payload": {
                    "private": False,
                    "to": "",
                    "message": "Hello, world!"
                }
            },
        )

    @freeze_time(test_dt_str)
    def test_connect_anon(self):

        notification = get_connected_notification("anonymus")

        self.assertDictEqual(
            notification.get_notification(),
            {
                "action": CommandType.connected,
                "datetime": str(datetime.now()),
                "payload": {"user_name": "anonymus"},
                "reason": "",
                "success": True,
            },
        )
