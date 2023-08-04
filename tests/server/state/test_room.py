import unittest

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
from chat.singleton import singleton

class TestRoomStore(unittest.TestCase):

    def tearDown(self) -> None:
        singleton.instances = {}

    def test_get_default(self):
        room = dataclasses.asdict(RoomStore().default_room())
        self.assertEqual(room['name'], 'Global')
        self.assertEqual(room['room_type'], RoomType.open)
        self.assertEqual(room['deleted'], False)
        self.assertListEqual(room['admins'], [])

    def test_room_store_public(self):
        user1 = UserStore().register(username='user1', password='123')
        user2 = UserStore().register(username='user2', password='123')

        room1 = RoomStore().add_room(
            room=Room(
                key=None,
                name='room1',
                room_type=RoomType.restricted,
                admins=[user1.username],
                allowed=[],
                deleted=False
            )
        )

        room2 = RoomStore().add_room(
            room=Room(
                key=None,
                name='room2',
                room_type=RoomType.open,
                admins=[user1.username],
                allowed=[],
                deleted=False
            )
        )

        self.assertTrue(RoomStore().user_in_room(username=user1.username, room=room1))   
        self.assertFalse(RoomStore().user_in_room(username=user2.username, room=room1))

        self.assertFalse(RoomStore().join(user=user2, room=room1))
        self.assertFalse(RoomStore().user_in_room(username=user2.username, room=room1))

        self.assertTrue(RoomStore().join(user=user2, room=room2))
        self.assertTrue(RoomStore().user_in_room(username=user2.username, room=room2))

        self.assertTrue(RoomStore().add_user_to_room(room=room1, admin=user1, new_user=user2))
        self.assertTrue(RoomStore().join(user=user2, room=room1))
        self.assertTrue(RoomStore().user_in_room(username=user2.username, room=room1))

        self.assertFalse(RoomStore().remove_user_from_room(room=room1, admin=user2, remove_user=user1))

        self.assertTrue(RoomStore().remove_user_from_room(room=room1, admin=user1, remove_user=user2))
        self.assertFalse(RoomStore().user_in_room(username=user2.username, room=room1))
        self.assertFalse(RoomStore().join(user=user2, room=room1))
        self.assertFalse(RoomStore().user_in_room(username=user2.username, room=room1))

        self.assertIsNotNone(RoomStore().get_room_by_name(room_name=room1.name))
        self.assertTrue(RoomStore().remove_user_from_room(room=room1, admin=user1, remove_user=user1))
        self.assertIsNone(RoomStore().get_room_by_name(room_name=room1.name))

    def test_room_store_private(self):
        user1 = UserStore().register(username='user1', password='123')
        user2 = UserStore().register(username='user2', password='123')
        user3 = UserStore().register(username='user3', password='123')

        room = RoomStore().add_room(
            room=Room(
                key=None,
                name='',
                room_type=RoomType.private,
                admins=[user1.username, user2.username],
                allowed=[],
                deleted=False
            )   
        )

        self.assertTrue(RoomStore().user_in_room(username=user1.username, room=room))   
        self.assertTrue(RoomStore().user_in_room(username=user2.username, room=room))

        self.assertTrue(RoomStore().user_is_admin(room=room, user=user1))
        self.assertFalse(RoomStore().add_user_to_room(room=room, admin=user1, new_user=user3))
        self.assertFalse(RoomStore().remove_user_from_room(room=room, admin=user1, remove_user=user2))

        self.assertTrue(RoomStore().leave(user=user1, room=room))
        self.assertFalse(RoomStore().user_in_room(username=user1.username, room=room))
        self.assertFalse(RoomStore().user_in_room(username=user2.username, room=room))
        self.assertIsNone(RoomStore().get_room_by_name(room_name=room.name))




