from dataclasses import dataclass
from typing import List

from ..singleton import singleton


@dataclass
class User:
    username: str
    key: str

    def validate(self, key) -> bool:
        
        if not key == self.key:
            return False
        
        return True
    

@singleton
class UserStore:
    def __init__(self) -> None:
        self.store: dict[str, User] = dict()

    def login(self, username, key) -> bool:
        """
        Returns true if only (username, key) is already in UserStore
        """
        for keyname, user in self.store.items():
            if not username == keyname:
                continue

            if user.validate(key):
                return True
            
        return False
    
    def register(self, username, key) -> bool:
        """
        Checks if username not in UserStore. If not registers.
        False if already exists; False if registers successfully.
        """

        for keyname in self.store.keys():
            if keyname == username:
                return False
            
        self.store[username] = User(username=username, key=key)
        return True


    def dump(self, path):
        """
        Dumps whole store in json format as it is without any encription.
        """
        pass

    def load(self, path):
        pass

    def get_user_list(self):
        return self.store.keys()