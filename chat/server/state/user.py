from dataclasses import dataclass
from typing import Dict
import json
import logging
from aiohttp import web
import uuid

from ...singleton import singleton
from ..manage_files import write_file, read_file, to_dict
from ...command_types import CommandType

from ...exceptions import (
    UsernameUnaceptable,
    UsernameAlreadyInUse,
    WeakPassword,
    NoRegistredUserFound
)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)




@dataclass
class User:

    username: str
    password: str

    def validate(self, password) -> bool:
        
        if not password == self.password:
            return False
          
        return True
    
    def __post_init__(self):
        if self.username.startswith('/'):
            raise UsernameUnaceptable
        
        if len(self.password) < 3:
            raise WeakPassword

@singleton
class UserStore:

    def __init__(self) -> None: 
        self.store: Dict[str, User] = dict()

    def get_user(self, username: str) -> User:
        try:
            return self.store[username]
        except KeyError:
            raise NoRegistredUserFound
    
    @staticmethod
    def __create_anonymus_name():
        return 'anonymus_' + str(uuid.uuid4().int)[:8]
    
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
        
        self.store[username] = User(username=username, password=password)
        return self.store[username]

    async def dump(self, path: str = './data/users.json'):
        """
        Dumps whole store in json format as it is without any encription.
        """
        data = to_dict(self.store)
        await write_file(path, json.dumps(data, indent=4))

    async def load(self, path: str = './data/users.json'):
        try:
            data = await read_file(path)

            for key, value in data.items():
                obj = json.loads(value)
                self.register(obj['username'], obj['password'])

        except Exception as ex:
            logger.error(f'Unable load users from {path}, because: {ex}.')

    def get_user_list(self):
        return self.store.keys()