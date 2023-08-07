import unittest

from mock import patch

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
    
    @patch('argon2.verify_password')
    def test_user_validate(self, verify_password):
        user = User(username="andrew", hashed_password="123")
        verify_password.return_value = False
        self.assertFalse(user.validate("vvv"))
        verify_password.return_value = True
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

    @patch('argon2.verify_password')
    def test_store_login(self, verify_password):
        UserStore().register(username="andrew", password="123")

        verify_password.return_value = False
        self.assertFalse(UserStore().login(username="andrew", password="1234"))
        verify_password.return_value = False
        self.assertFalse(UserStore().login(username="andrew1", password="123"))
        verify_password.return_value = True
        self.assertTrue(UserStore().login(username="andrew", password="123"))

        self.assertFalse(UserStore().logout(username="andr"))
        self.assertTrue(UserStore().logout(username="andrew"))


if __name__ == "__main__":
    unittest.main()
