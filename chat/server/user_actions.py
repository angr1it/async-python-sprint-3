from typing import Dict
import logging
from datetime import datetime
from datetime import datetime


from chat.command_types import CommandType
from chat.utils.my_response import WSResponse
from chat.exceptions import (
    UnsuitableCommand,
    BadRequest,
)
from chat.server.state.meta import Meta
from chat.server.state.user import UserStore
from chat.server.state.message import NotificationStore, UserAction, Action
from chat.server.command import Command

logger = logging.getLogger()

INCORRECT_AUTH = "Incorrect username or password."
REGISTER_FAIL = "The specified username is already taken."
ALREADY_LOGGED_IN = "Already logged in."
ALREADY_LOGGED_OUT = "Already logged out."


class RegisterAction(Command):
    @staticmethod
    def __get_notification(username, success, reason=None):
        if not reason:
            reason = ""

        return Action(
            action=CommandType.register,
            datetime=str(datetime.now()),
            expired=False,
            success=success,
            reason="",
            payload={"user_name": username},
        )

    @classmethod
    async def run(
        cls,
        ws_response: WSResponse,
        meta: Meta,
        command: str = None,
        message_json: Dict[str, str] = None,
    ):
        if not command == CommandType.register:
            raise UnsuitableCommand

        try:
            username = message_json["username"]
            password = message_json["password"]
        except KeyError:
            raise BadRequest

        if meta.loggedin:
            await NotificationStore().process(
                ws=ws_response,
                notification=RegisterAction.__get_notification(
                    username=username, success=False, reason=ALREADY_LOGGED_IN
                ),
            )
            return meta

        if (
            UserStore().register(username=username, password=password).username
            == username
        ):
            await NotificationStore().process(
                ws=ws_response,
                notification=RegisterAction.__get_notification(
                    username=username, success=True, reason=""
                ),
            )
            return meta

        await NotificationStore().process(
            ws=ws_response,
            notification=RegisterAction.__get_notification(
                username=username, success=False, reason=REGISTER_FAIL
            ),
        )

        return meta


class LoginAction(Command):
    @staticmethod
    def __get_notification(username, success, reason=None):
        if not reason:
            reason = ""

        return UserAction(
            action=CommandType.login,
            datetime=str(datetime.now()),
            expired=False,
            success=success,
            reason=reason,
            user_name=username,
            payload={},
        )

    @classmethod
    async def run(
        cls,
        ws_response: WSResponse,
        meta: Meta,
        command: str = None,
        message_json: Dict[str, str] = None,
    ):
        if not command == CommandType.login:
            raise UnsuitableCommand

        if meta.loggedin:
            await NotificationStore().process(
                ws=ws_response,
                notification=LoginAction.__get_notification(
                    username=meta.user_name,
                    success=False,
                    reason=ALREADY_LOGGED_IN
                ),
            )
            return meta

        try:
            username = message_json["username"]
            password = message_json["password"]
        except KeyError:
            raise BadRequest

        if UserStore().login(username=username, password=password):
            await NotificationStore().process(
                ws=ws_response,
                notification=LoginAction.__get_notification(
                    username=username, success=True, reason=""
                ),
            )

            meta.user_name = username
            meta.loggedin = True
            return meta

        await NotificationStore().process(
            ws=ws_response,
            notification=LoginAction.__get_notification(
                username=meta.user_name, success=False, reason=INCORRECT_AUTH
            ),
        )

        return meta


class LogoutAction(Command):
    @classmethod
    async def run(
        cls,
        ws_response: WSResponse,
        meta: Meta,
        command: str = None,
        message_json: Dict[str, str] = None,
    ):
        if not command == CommandType.logout:
            raise UnsuitableCommand

        if not meta.loggedin:
            await NotificationStore().process(
                ws=ws_response,
                notification=UserAction(
                    action=CommandType.logout,
                    datetime=str(datetime.now()),
                    expired=False,
                    success=False,
                    reason=ALREADY_LOGGED_OUT,
                    user_name=meta.user_name,
                    payload={},
                ),
            )
            return meta

        user_before = meta.user_name
        if UserStore().logout(username=meta.user_name):
            meta.user_name = UserStore().get_anonymus_name()
            meta.loggedin = False

            await NotificationStore().process(
                ws=ws_response,
                notification=UserAction(
                    action=CommandType.logout,
                    datetime=str(datetime.now()),
                    expired=False,
                    success=True,
                    reason="",
                    user_name=user_before,
                    payload={},
                ),
            )
            return meta

        raise BadRequest
