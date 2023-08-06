import unittest

from chat.server.state.user import (
    User,
    UserStore,
    WeakPassword,
    UsernameAlreadyInUse,
    UsernameUnaceptable,
)
from chat.singleton import singleton


class TestUserStore(unittest.TestCase):
    def tearDown(self) -> None:
        singleton.instances = {}

    def test_user(self):
        self.assertRaises(UsernameUnaceptable, User, "/andrew", "12")
        self.assertRaises(WeakPassword, User, "andrew", "12")

    def test_user_validate(self):
        user = User(username="andrew", password="123")
        self.assertFalse(user.validate("vvv"))
        self.assertTrue(user.validate("123"))

    def test_store_register(self):
        self.assertRaises(WeakPassword, UserStore().register, "andrew", "12")
        self.assertRaises(
            UsernameUnaceptable, UserStore().register, "/andrew", "1223"
        )
        UserStore().register(username="andrew", password="123")
        self.assertRaises(
            UsernameAlreadyInUse, UserStore().register, "andrew", "1234"
        )

    def test_store_login(self):
        UserStore().register(username="andrew", password="123")

        self.assertFalse(UserStore().login(username="andrew", password="1234"))
        self.assertFalse(UserStore().login(username="andrew1", password="123"))
        self.assertTrue(UserStore().login(username="andrew", password="123"))

        self.assertFalse(UserStore().logout(username="andr"))
        self.assertTrue(UserStore().logout(username="andrew"))


if __name__ == "__main__":
    unittest.main()
