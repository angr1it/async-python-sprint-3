from typing import Dict
import logging

from chat.utils.my_response import WSResponse
from chat.command_types import CommandType
from chat.exceptions import (
    UnsuitableCommand,
    BadRequest,
    NoRegistredUserFound,
)
from chat.server.state.meta import Meta
from chat.server.state.room import RoomStore
from chat.server.state.user import UserStore
from chat.server.state.message import (
    NotificationStore,
    get_message_notification
)
from chat.server.command import Command


logger = logging.getLogger()


class SendAction(Command):
    @classmethod
    async def run(
        cls,
        ws_response: WSResponse,
        meta: Meta,
        command: str = None,
        message_json: Dict[str, str] = None,
    ):
        if not command == CommandType.send:
            raise UnsuitableCommand

        if message_json is None:
            raise ValueError

        try:
            message = message_json["message"]
            room_name = message_json["room"]
            private = bool(message_json["private"])
            to_user = message_json["to_user"]
        except (KeyError, ValueError):
            raise BadRequest

        await NotificationStore().process(
            ws=ws_response,
            notification=get_message_notification(
                room_name=room_name,
                user_name=meta.user_name,
                success=True,
                reason="",
                private=private,
                to=to_user,
                message=message,
            )
        )

        return meta


class HistoryAction(Command):
    @classmethod
    async def run(
        cls,
        ws_response: WSResponse,
        meta: Meta,
        command: str = None,
        message_json: Dict[str, str] = None,
    ):
        if not command == CommandType.history:
            raise UnsuitableCommand

        try:
            room = message_json["room"]
            notification_count = message_json["notification_count"]

        except KeyError:
            raise BadRequest

        if room is None:
            room = ""

        if room == "":
            if not meta.loggedin:
                raise NoRegistredUserFound

            await NotificationStore().history_user(
                ws=ws_response,
                user=UserStore().get_user(username=meta.user_name),
                n=notification_count,
            )
            return meta

        await NotificationStore().history_room(
            ws=ws_response,
            user_name=meta.user_name,
            room=RoomStore().get_room_by_name(room_name=room),
            n=notification_count,
        )

        return meta
