from typing import Dict
import logging
from datetime import datetime
import dataclasses
from aiohttp import web
import aiofiles
from datetime import datetime

logger = logging.getLogger()

from ..command_types import CommandType

from ..exceptions import (
    UnsuitableCommand,
    BadRequest,
)

from .state.meta import Meta
from .state.room import RoomStore
from .state.user import UserStore
from .state.message import (
    NotificationStore,
    Register as RegisterNotification,
    Login as LoginNotification,
    Logout as LogoutNotification
)

from .command import Command

INCORRECT_LOGIN_COMBINATION = 'Incorrect username or password.'
REGISTER_FAIL = 'The specified username is already taken.'
ALREADY_LOGGED_IN = 'Already logged in.'
ALREADY_LOGGED_OUT = 'Already logged out.'

class Register(Command):
    
    @classmethod
    async def run(cls, ws_response: web.WebSocketResponse, meta: Meta, command: str = None, message_json: Dict[str, str] = None):
        if not command == CommandType.register:
            raise UnsuitableCommand
        
        try:
            username = message_json['username']
            password = message_json['password']
        except:
            raise BadRequest
        
        if meta.loggedin:
            await NotificationStore().process(
                ws=ws_response,
                notification=RegisterNotification(
                    action=CommandType.register, datetime=datetime.now(), username=username, success=False, reason=ALREADY_LOGGED_IN, expired=False
                )
            )
            return meta

        if UserStore().register(username=username, password=password).username == username:
            await NotificationStore().process(
                ws=ws_response,
                notification=RegisterNotification(
                    action=CommandType.register, datetime=datetime.now(), username=username, success=True, reason='', expired=False
                )
            )
            return meta
        
        await NotificationStore().process(
            ws=ws_response,
            notification=RegisterNotification(
                action=CommandType.register, datetime=datetime.now(), username=username, success=False, reason=REGISTER_FAIL, expired=False
                )
            )

        return meta


class Login(Command):
    @classmethod
    async def run(cls, ws_response: web.WebSocketResponse, meta: Meta, command: str = None, message_json: Dict[str, str] = None):
        if not command == CommandType.login:
            raise UnsuitableCommand

        if meta.loggedin:
            await NotificationStore().process(
                ws=ws_response,
                notification=LoginNotification(
                    action=CommandType.login, datetime=datetime.now(), expired=False, user_name=meta.user_name, success=False, reason=ALREADY_LOGGED_IN
                )
            )
            return meta
        
        try:
            username = message_json['username']
            password = message_json['password']
        except:
            raise BadRequest

        if UserStore().login(username=username, password=password):
            await NotificationStore().process(
                ws=ws_response,
                notification=LoginNotification(
                    action=CommandType.login, datetime=datetime.now(), expired=False, user_name=username, success=True, reason=''
                )
            )
            
            meta.user_name = username
            meta.loggedin = True
            return meta

        await NotificationStore().process(
            ws=ws_response,
            notification=LoginNotification(
                action=CommandType.login, datetime=datetime.now(), expired=False, user_name=username, success=False, reason=INCORRECT_LOGIN_COMBINATION
            )
        )

        return meta


class Logout(Command):
    @classmethod
    async def run(cls, ws_response: web.WebSocketResponse, meta: Meta, command: str = None, message_json: Dict[str, str] = None):
        if not command == CommandType.logout:
            raise UnsuitableCommand
        
        if not meta.loggedin:
            await NotificationStore().process(
                ws=ws_response,
                notification=LogoutNotification(
                    action=CommandType.logout, datetime=datetime.now(), expired=False, user_name=meta.user_name, success=False, reason=ALREADY_LOGGED_OUT
                )
            )
            return meta

        if UserStore().logout(username=meta.user_name):

            meta.user_name = UserStore().get_anonymus_name()
            meta.loggedin = False

            await NotificationStore().process(
                ws=ws_response,
                notification=LogoutNotification(
                    action=CommandType.logout, datetime=datetime.now(), expired=False, user_name=meta.user_name, success=True, reason=''
                )
            )
            return meta

        raise BadRequest
