from dataclasses import dataclass
import json
import logging
import uuid

import argon2

from chat.singleton import singleton
from chat.manage_files import write_file, read_file, to_dict

from chat.exceptions import (
    UsernameUnaceptable,
    UsernameAlreadyInUse,
    WeakPassword,
    NoRegistredUserFound,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class User:
    username: str
    hashed_password: bytes
    hashed: bool = False

    def validate(self, password) -> bool:
        if not argon2.verify_password(
            hash=self.hashed_password,
            password=bytes(password, encoding='utf-8')
        ):
            return False

        return True

    def __post_init__(self):
        if self.username.startswith("/"):
            raise UsernameUnaceptable

        if len(self.hashed_password) < 3:
            raise WeakPassword

        if not self.hashed:
            self.hashed_password = argon2.hash_password(bytes(
                self.hashed_password, encoding='utf-8'
            ))
            self.hashed = True


@singleton
class UserStore:
    def __init__(self) -> None:
        self.store: dict[str, User] = dict()

    def get_user(self, username: str) -> User:
        try:
            return self.store[username]
        except KeyError:
            raise NoRegistredUserFound

    @staticmethod
    def __create_anonymus_name():
        return "anonymus_" + str(uuid.uuid4().int)[:8]

    def get_anonymus_name(self):
        name = self.__create_anonymus_name()

        while name in self.store.keys():
            name = self.__create_anonymus_name()

        return name

    def login(self, username: str, password: str) -> bool:
        """
        Returns true if only (username, key) is already in UserStore;
        Broadcasts notification due app;
        """
        for keyname, user in self.store.items():
            if not username == keyname:
                continue

            if user.validate(password):
                return True

        return False

    def logout(self, username: str) -> bool:
        if username in self.store.keys():
            return True

        return False

    def register(self, username: str, password: str) -> User:
        """
        Checks if username not in UserStore. If not registers;
        False if already exists; False if registers successfully;
        Broadcasts notification due app;

        """

        if username in self.store.keys():
            raise UsernameAlreadyInUse

        self.store[username] = User(
            username=username,
            hashed_password=password
        )
        return self.store[username]

    async def dump(self, path: str = "./data/users.json"):
        """
        Dumps whole store in json format as it is without any encription.
        """
        data = to_dict(self.store)
        await write_file(path, json.dumps(data, indent=4))

    async def load(self, path: str = "./data/users.json"):
        try:
            data = await read_file(path)

            for key, value in data.items():
                obj = json.loads(value)
                self.store[obj["username"]] = User(
                    username=obj["username"],
                    hashed_password=bytes(
                        obj["hashed_password"],
                        encoding='utf-8'
                    ),
                    hashed=True
                )

        except Exception as ex:
            logger.error(f"Unable load users from {path}, because: {ex}.")

    def get_user_list(self):
        return self.store.keys()
