from typing import Tuple
from aiohttp import web
from dataclasses import dataclass
from enum import Enum
import uuid
from typing import List, Dict

from ...singleton import singleton
from .user import User
from .meta import Meta
from ...exceptions import *

DEFAULT_ROOM = 'Global'


class RoomType(str, Enum):
    private = '/private'
    restricted = '/restricted'
    open = '/open'


@dataclass
class Room:

    key: str
    name: str
    room_type: RoomType

    admins: List[str]
    allowed: List[str]

    deleted: bool

    def __post_init__(self):
        self.key = uuid.uuid4()

        for admin in self.admins:
            if not admin in self.allowed:
                self.allowed.append(admin)

@singleton
class RoomStore:
    def __init__(self) -> None:
        self.store: Dict[str, Room] = {}

        global_room =Room(
            key=None,
            name=DEFAULT_ROOM,
            room_type=RoomType.open,
            admins=[],
            allowed=[],
            deleted=False
        )

        self.store[global_room.key] = global_room 

        self.key_by_name: Dict[str, str] = {}
        self.key_by_name[DEFAULT_ROOM] = global_room.key

        self.private_keys: Dict[frozenset, str] = {}

        self.user_rooms: Dict[str, List[str]] = {}

    def __add_room_to_user(self, usename: str, room: Room) -> None:
        try:
            self.user_rooms[usename].append(room.key)
        except KeyError:
            self.user_rooms[usename] = list()
            self.user_rooms[usename].append(room.key)
    
    def __allowed_to_join(self, username: str, room: Room) -> bool:
        if room.room_type == RoomType.open:
            return True
        
        if room.room_type == RoomType.private:
            return False
        
        return username in room.allowed
    
    def get_rooms_by_user(self, user: User) -> List[Room]:
        
        try:
            rooms_keys = self.user_rooms[user.username]
            rooms = [self.store[key] for key in rooms_keys if self.store[key].deleted == False]
            rooms.insert(self.default_room(), 0)
            return rooms
        except:
            raise NotImplementedError

    def user_in_room(self, user: User, room: Room) -> bool:
        """
        Supposed to be called every time, user trying to write in room.
        """
        if room == self.store[self.key_by_name[DEFAULT_ROOM]]:
            return True
        
        try:
            if room.key in self.user_rooms[user.username]:
                return True
        except:
            return False
        
        return False
    
    def default_room(self):
        return self.store[self.key_by_name[DEFAULT_ROOM]]

    def add_room(self, room: Room) -> Room:
        
        if room.room_type == RoomType.private:
            if not len(room.admins) == 2:
                raise ValueError
            
            pair = frozenset((room.admins[0], room.admins[1]))

            if pair in self.private_keys.keys():
                
                key = self.private_keys[pair]
                
                if self.store[key].deleted:
                    self.store[key].deleted = False
                    return self.store[key]
                
                raise DialogueOpenedAlready

            self.private_keys[pair] = room.key
            self.store[room.key] = room

            for user in room.admins:
                self.__add_room_to_user(usename=user, room=room)

            return room


        self.key_by_name[room.name] = room.key
        self.store[room.key] = room

        for user in room.admins:
            self.__add_room_to_user(usename=user, room=room)

        return room

    def user_is_admin(self, room: Room, user: User) -> bool:

        if user.username in room.admins:
            return True
        
        return False
    
    def delete_room(self, room: Room, admin: User) -> bool:
        
        if not self.user_is_admin(room=room, user=admin):
            return False
        
        room.deleted = True

        if room.room_type == RoomType.private:
            del self.private_keys[frozenset(room.admins[0], room.admins[1])]
        else:
            del self.key_by_name[room.name]
        
        for user in room.allowed:
            try:
                self.user_rooms[user].remove(room.key)
            except:
                pass

        return True

    def add_user_to_room(self, room: Room, admin: User, new_user: User) -> bool:
        
        if room.room_type == RoomType.private:
            return False
        
        if room.room_type == RoomType.open:
            return True
        
        if not self.user_is_admin(room=room, user=admin):
            return False
        
        room.allowed.append(new_user.username)
        return True

    def remove_user_from_room(self, room: Room, admin: User, remove_user: User) -> bool:
        
        if room.room_type == RoomType.private:
            return False
        
        if room.room_type == RoomType.open:
            # TODO: add blocking/ban here
            return False
        
        if not self.user_is_admin(room=room, user=admin):
            return False
        
        self.leave(user=remove_user, room=room)
        
        try:
            room.allowed.remove(remove_user.username)
        except ValueError:
            pass
        finally:
            return True
    
    def get_room_by_name(self, room_name: str) -> Room:
        """
        Trying to find a room; Returns room.
        """
        
        try:
            key = self.key_by_name[room_name]
            return self.store[key]
        except:
            return None

    def get_room_by_key(self, room_key: str) -> Room:
        """
        Tryes to find and return room. Returns None if unsuccessful.
        """
        try:
            return self.store[room_key]
        except KeyError:
            return None

    def find_private_room(self, user1: User, user2: User) -> Room:
        """
        Trying to find private room between two users. Returns key.

        """
        try:
            pair = frozenset((user1.username, user2.username))
            key_room = self.private_keys[pair]
            return self.store[key_room]
        except:
            raise NotImplementedError

    def join(self, user: User, room: Room) -> bool:
        """
        Checks if user already inside current room;
        If so, sends False;
        If not, tries to join;

        Assesses if user is allowed to go inside of new room.
        """

        if room.room_type == RoomType.private:
            return False
        
        if self.__allowed_to_join(username=user.username, room=room):
            self.__add_room_to_user(usename=user.username, room=room)
            return True
        
        return False

    def leave(self, user: User, room: Room) -> bool:
        """
        User leaves the room; User can't leave default room.
        """
        
        if room == self.default_room():
            return False
        
        if not room.key in self.user_rooms[user.username]:
            return False
        
        if room.room_type == RoomType.private:
            room.deleted = True
            self.user_rooms[room.allowed[0]].remove(room.key)
            self.user_rooms[room.allowed[1]].remove(room.key)

            return True

        if (len(room.admins) == 1 and self.user_is_admin(room=room, user=user)) or room.room_type == RoomType.private:
            self.delete_room(room=room, admin=user)
            return True
        
        self.user_rooms[user.username].remove(room.key)
        return True

    def dump(self, path: str) -> bool:
        """
        Dumps all the data necessary for future load.
        """
        pass

    def load(self, path: str) -> bool:
        """
        Tryes to load saved file in order to restore state.
        """
        pass
