from datetime import datetime
from enum import Enum

from chat.command_types import CommandType


test_dt_str = "2023-01-01"
test_dt = str(datetime.strptime(test_dt_str, "%Y-%m-%d"))


class SendRequests(Enum):
    SEND_COMMAND = "Global hello"
    SEND_JSON_REQ = {
        "command": "/send",
        "message": "hello",
        "room": "Global",
        "private": False,
        "to_user": "/all",
    }
    SEND_JSON_RESP = {
        "action": CommandType.send,
        "success": True,
        "reason": "",
        "datetime": test_dt,
        "user": "andre",
        "room_name": "Global",
        "payload": {"private": False, "to": "/all", "message": "hello"},
    }

    SEND_PRIVATE_COMMAND = "user2 hello"
    SEND_PRIVATE_JSON_REQ = {
        "command": "/send",
        "message": "hello",
        "room": "",
        "private": True,
        "to_user": "user2",
    }


class HistoryRequests(Enum):
    COMMAND = "1 Global"
    JSON_REQ = {
        "command": "/history", "room": "Global", "notification_count": 1
    }
    JSON_RESP = {
        "action": CommandType.history,
        "success": True,
        "reason": "",
        "datetime": test_dt,
        "user": "andre",
        "payload": {"history": [SendRequests.SEND_JSON_RESP.value]},
    }

    USER_COMMAND = "10"
    USER_DEFAULT_COMMAND = " "
    USER_JSON_REQ = {
        "command": "/history", "room": "", "notification_count": 10
    }
    USER_DEFAULT_JSON_REQ = {
        "command": "/history",
        "room": "",
        "notification_count": 20,
    }

    HISTORY_USER_DEFAULT_USER_JSON_RESP = {
        "action": CommandType.history,
        "success": True,
        "reason": "",
        "datetime": test_dt,
        "user": "andre",
        "payload": {
            "history": [
                {
                    "action": CommandType.create_room,
                    "success": True,
                    "reason": "",
                    "datetime": test_dt,
                    "user": "andre",
                    "payload": {"room_name": "open_room"},
                }
            ]
        },
    }


class RegisterRequests(Enum):
    COMMAND = "user1 123"
    JSON_REQ = {"command": "/register", "username": "user1", "password": "123"}
    JSON_RESP = {
        "action": CommandType.register,
        "datetime": test_dt,
        "success": True,
        "reason": "",
        "payload": {"user_name": "user1"},
    }


class LoginRequests(Enum):
    COMMAND = "user1 123"
    JSON_REQ = {"command": "/login", "username": "user1", "password": "123"}
    JSON_REQ_BAD = {
        "command": "/login", "username": "user1", "password": "1234"
    }
    JSON_RESP = {
        "action": CommandType.login,
        "success": True,
        "reason": "",
        "datetime": test_dt,
        "user": "user1",
        "payload": {},
    }
    LOGIN_JSON_RESP_BAD = {
        "action": CommandType.login,
        "success": False,
        "reason": "Incorrect username or password.",
        "datetime": test_dt,
        "user": "anonymus_12314",
        "payload": {},
    }
    LOGIN_JSON_RESP_AGAIN = {
        "action": CommandType.login,
        "success": False,
        "reason": "Already logged in.",
        "datetime": test_dt,
        "user": "user1",
        "payload": {},
    }


class LogoutRequests(Enum):
    LOGOUT_COMMAND = ""
    LOGOUT_JSON_REQ = {"command": "/logout"}
    LOGOUT_JSON_RESP = {
        "action": "/logout",
        "success": True,
        "datetime": test_dt,
        "user": "anonymus_22379152",
        "reason": "",
    }


class CreateOpenRoomRequests(Enum):
    CREATE_COMMAND = "open_room /open"
    CREATE_JSON_REQ = {
        "command": CommandType.create_room,
        "room_name": "open_room",
        "room_type": "/open",
    }
    CREATE_JSON_RESP_ANON = {
        "action": CommandType.create_room,
        "success": False,
        "reason": "Not authorized.",
        "datetime": test_dt,
        "user": "anonymus_12314",
        "payload": {"room_name": "open_room"},
    }
    CREATE_JSON_RESP_SUCCESS = {
        "action": CommandType.create_room,
        "success": True,
        "reason": "",
        "datetime": test_dt,
        "user": "user1",
        "payload": {"room_name": "open_room"},
    }

    DELETE_COMMAND = "open_room"
    DELETE_JSON_REQ = {
        "command": CommandType.delete_room, "room_name": "open_room"
    }
    DELETE_JSON_RESP_ANON = {
        "action": CommandType.delete_room,
        "success": False,
        "reason": "Not authorized.",
        "datetime": test_dt,
        "user": "anonymus_12314",
        "payload": {"room_name": "open_room"},
    }
    DELETE_JSON_RESP_SUCCESS = {
        "action": CommandType.delete_room,
        "success": True,
        "reason": "",
        "datetime": test_dt,
        "user": "user1",
        "payload": {"room_name": "open_room"},
    }


class JoinOpenRequests(Enum):
    COMMAND = "open_room"
    REQ = {"command": CommandType.join_room, "room_name": "open_room"}
    RESP_ANON = {
        "action": CommandType.join_room,
        "success": False,
        "reason": "Not allowed to join this room.",
        "datetime": test_dt,
        "user": "anonymus_12314",
        "payload": {"room_name": "open_room"},
    }
    RESP_SUCESS = {
        "action": CommandType.join_room,
        "success": True,
        "reason": "",
        "datetime": test_dt,
        "user": "user2",
        "payload": {"room_name": "open_room"},
    }


class RestrictedRoomRequests(Enum):
    CREATE_COMMAND = "restricted_room /restricted"
    ADD_USER_COMMAND = "restricted_room user2"
    REMOVE_USER_COMMAND = "restricted_room user2"
    LEAVE_COMMAND = "restricted_room"

    CREATE_ROOM_REQ = {
        "command": CommandType.create_room,
        "room_name": "restricted_room",
        "room_type": "/restricted",
    }
    ADD_USER_REQ = {
        "command": CommandType.add_user,
        "room_name": "restricted_room",
        "new_user": "user2",
    }
    JOIN_REQ = {
        "command": CommandType.join_room, "room_name": "restricted_room"
    }
    REMOVE_USER_REQ = {
        "command": CommandType.remove_user,
        "room_name": "restricted_room",
        "remove_user": "user2",
    }
    LEAVE_REQ = {
        "command": CommandType.leave_room, "room_name": "restricted_room"
    }

    CREATE_ROOM_RESP_SUCCESS = {
        "action": CommandType.create_room,
        "success": True,
        "reason": "",
        "datetime": test_dt,
        "user": "user1",
        "payload": {"room_name": "restricted_room"},
    }
    ADD_USER_RESP_NOT_ALLOWED = {
        "action": CommandType.add_user,
        "success": False,
        "reason": "Not allowed.",
        "datetime": test_dt,
        "user": "user2",
        "payload": {"room_name": "restricted_room", "new_user": "user2"},
    }
    ADD_USER_RESP_NO_AUTH = {
        "action": CommandType.add_user,
        "success": False,
        "reason": "Not authorized.",
        "datetime": test_dt,
        "user": "anonymus_12314",
        "payload": {"room_name": "restricted_room", "new_user": "user2"},
    }
    ADD_USER_RESP_SUCCESS = {
        "action": CommandType.add_user,
        "success": True,
        "reason": "",
        "datetime": test_dt,
        "user": "user1",
        "payload": {"room_name": "restricted_room", "new_user": "user2"},
    }
    JOIN_RESP_ANON = {
        "action": CommandType.join_room,
        "success": False,
        "reson": "Not allowed to join this room.",
        "datetime": test_dt,
        "user": "anonymus_12314",
        "room_name": "restricted_room",
    }
    JOIN_RESP_SUCCESS = {
        "action": CommandType.join_room,
        "success": True,
        "reason": "",
        "datetime": test_dt,
        "user": "user2",
        "payload": {"room_name": "restricted_room"},
    }
    REMOVE_USER_RESP_ANON = {
        "action": CommandType.remove_user,
        "success": False,
        "reason": "Not allowed.",
        "datetime": test_dt,
        "user": "anonymus_12314",
        "payload": {"room_name": "restricted_room", "remove_user": "user2"},
    }
    REMOVE_USER_RESP_SUCCESS = {
        "action": CommandType.remove_user,
        "success": True,
        "reason": "",
        "datetime": test_dt,
        "user": "user1",
        "payload": {"room_name": "restricted_room", "remove_user": "user2"},
    }
    LEAVE_ROOM = {
        "action": CommandType.leave_room,
        "datetime": test_dt,
        "success": True,
        "reason": "",
        "room_name": "restricted_room",
        "remove_user": "user2",
    }


class OpenDialogueRequests(Enum):
    OPEN_COMMAND = "user1"
    OPEN_JSON_REQ = {
        "command": CommandType.open_dialogue, "with_user": "user1"
    }
    OPEN_JSON_RESP_SUCCESS = {
        "action": CommandType.open_dialogue,
        "success": True,
        "reason": "",
        "datetime": test_dt,
        "user": "user2",
        "payload": {"with_user": "user1"},
    }

    DELETE_COMMAND = "user2"
    DELETE_JSON_REQ = {
        "command": CommandType.delete_dialogue, "with_user": "user2"
    }
    DELETE_JSON_RESP_ERR = {
        "action": CommandType.delete_dialogue,
        "success": False,
        "reason": "No dialogue found.",
        "datetime": test_dt,
        "user": "user3",
        "payload": {"with_user": "user2"},
    }
    DELETE_JSON_RESP_SUCCESS = {
        "action": CommandType.delete_dialogue,
        "success": True,
        "reason": "",
        "datetime": test_dt,
        "user": "user1",
        "payload": {"with_user": "user2"},
    }
