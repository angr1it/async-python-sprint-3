from datetime import datetime
from enum import Enum

from chat.command_types import CommandType
from .server.state.room import RoomType



test_dt_str = '2023-01-01 00:00:00'
test_dt = str(datetime.strptime(test_dt_str, '%Y-%m-%d %H:%M:%S'))

class SendRequests(Enum):
    SEND_COMMAND = 'Global /all False hello'
    SEND_JSON_REQ = {'command': '/send', 'message': 'hello', 'room': 'Global', 'private': False, 'to_user': '/all'}
    SEND_JSON_RESP = {'action': '/send', 'datetime': test_dt, 'private': False, 'room': 'Global', 'from': 'andre', 'to': '/all', 'message': 'hello'}

class HistoryRequests(Enum):
    HISTORY_COMMAND = 'Global 1'
    HISTORY_JSON_REQ = {'command': '/history', 'room': 'Global', 'n': 1}   
    HISTORY_JSON_RESP = {'action': '/history', 'datetime': test_dt, 'success': True, 'reason': '', 'messages': [SendRequests.SEND_JSON_RESP.value]}

class RegisterRequests(Enum):
    REGISTER_COMMAND = 'user1 123'
    REGISTER_JSON_REQ = {'command': '/register', 'username': 'user1', 'password': '123'}
    REGISTER_JSON_RESP = {'action': '/register', 'datetime': test_dt, 'success': True, 'user': 'user1', 'reason': ''}

class LoginRequests(Enum):
    LOGIN_COMMAND = 'user1 123'
    LOGIN_JSON_REQ = {'command': '/login', 'username': 'user1', 'password': '123'}
    LOGIN_JSON_REQ_BAD = {'command': '/login', 'username': 'user1', 'password': '1234'}
    LOGIN_JSON_RESP = {'action': '/login', 'success': True, 'datetime': test_dt, 'user': 'user1', 'reason': ''}
    LOGIN_JSON_RESP_BAD = {'action': '/login', 'success': False, 'datetime': test_dt, 'user': 'user1', 'reason': 'Incorrect username or password.'}
    LOGIN_JSON_RESP_AGAIN = {'action': '/login', 'success': False, 'datetime': test_dt, 'user': 'user1', 'reason': 'Already logged in.'}

class LogoutRequests(Enum):
    LOGOUT_COMMAND = ''
    LOGOUT_JSON_REQ = {'command': '/logout'}
    LOGOUT_JSON_RESP = {'action': '/logout', 'success': True, 'datetime': test_dt, 'user': 'anonymus_22379152', 'reason': ''}

class CreateOpenRoomRequests(Enum):
    COMMAND = 'open_room /open'
    JSON_REQ = {'command': CommandType.create_room, 'room_name': 'open_room', 'room_type': '/open'}
    JSON_RESP_ANON = {'action': CommandType.create_room, 'datetime': test_dt, 'success': False, 'reason': 'Not authorized.', 'room_name': 'open_room'}
    JSON_RESP_SUCCESS = {'action': CommandType.create_room, 'datetime': test_dt, 'success': True, 'reason': '', 'room_name': 'open_room', 'admins': ['user1'], 'allowed': ['user1']}

class JoinOpenRequests(Enum):
    COMMAND = 'open_room'  
    REQ = {'command': CommandType.join_room, 'room_name': 'open_room'}
    RESP_ANON = {'action': CommandType.join_room, 'success': False, 'reson': 'Not allowed to join this room.', 'datetime': test_dt, 'user': 'anonymus_12314', 'room_name': 'open_room'}
    RESP_SUCESS = {'action': CommandType.join_room, 'success': True, 'reson': '', 'datetime': test_dt, 'user': 'user2', 'room_name': 'open_room'}

class RestrictedRoomRequests(Enum):
    CREATE_COMMAND = 'restricted_room /restricted'
    ADD_USER_COMMAND = 'restricted_room user2'
    REMOVE_USER_COMMAND = 'restricted_room user2'
    LEAVE_COMMAND = 'restricted_room'
    CREATE_ROOM_REQ = {'command': CommandType.create_room, 'room_name': 'restricted_room', 'room_type': '/restricted'}
    ADD_USER_REQ = {'command': CommandType.add_user, 'room_name': 'restricted_room', 'new_user': 'user2'}
    JOIN_REQ = {'command': CommandType.join_room, 'room_name': 'restricted_room'}
    REMOVE_USER_REQ = {'command': CommandType.remove_user, 'room_name': 'restricted_room', 'remove_user': 'user2'}
    LEAVE_REQ = {'command': CommandType.leave_room, 'room_name': 'restricted_room'}

    CREATE_ROOM_RESP_SUCCESS = {'action': CommandType.create_room, 'datetime': test_dt, 'success': True, 'reason': '', 'room_name': 'restricted_room', 'admins': ['user1'], 'allowed': ['user1']}
    ADD_USER_RESP_NOT_ALLOWED = {'action': CommandType.add_user, 'datetime': test_dt, 'success': False, 'reason': 'Not allowed.', 'room_name': 'restricted_room', 'new_user': 'user2'}
    ADD_USER_RESP_NO_AUTH = {'action': CommandType.add_user, 'datetime': test_dt, 'success': False, 'reason': 'Not authorized.', 'room_name': 'restricted_room', 'new_user': 'user2'}
    ADD_USER_RESP_SUCCESS = {'action': CommandType.add_user, 'datetime': test_dt, 'success': True, 'reason': '', 'room_name': 'restricted_room', 'new_user': 'user2'}
    JOIN_RESP_ANON = {'action': CommandType.join_room, 'success': False, 'reson': 'Not allowed to join this room.', 'datetime': test_dt, 'user': 'anonymus_12314', 'room_name': 'restricted_room'}
    JOIN_RESP_SUCCESS = {'action': CommandType.join_room, 'success': True, 'reson': '', 'datetime': test_dt, 'user': 'user2', 'room_name': 'restricted_room'}
    REMOVE_USER_RESP_ANON = {'action': CommandType.remove_user, 'datetime': test_dt, 'success': False, 'reason': 'Not allowed.', 'room_name': 'restricted_room', 'remove_user': 'user2'}
    REMOVE_USER_RESP_SUCCESS = {'action': CommandType.remove_user, 'datetime': test_dt, 'success': True, 'reason': '', 'room_name': 'restricted_room', 'remove_user': 'user2'}
    LEAVE_ROOM_SUCCESS = {'action': CommandType.leave_room, 'datetime': test_dt, 'success': True, 'reason': '', 'room_name': 'restricted_room', 'remove_user': 'user2'}