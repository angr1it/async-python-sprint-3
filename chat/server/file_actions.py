from typing import Dict
import logging
from datetime import datetime

from chat.utils.my_response import WSResponse
from chat.command_types import CommandType
from chat.exceptions import (
    UnsuitableCommand,
    BadRequest,
)
from chat.server.state.meta import Meta
from chat.server.state.message import NotificationStore, UserAction
from chat.server.state.file import FileStore
from chat.server.command import Command
from chat.manage_files import send_file

logger = logging.getLogger()


class LoadFileAction(Command):
    @staticmethod
    def get_load_file_notification(
        user_name: str, filename: str, success: str, reason: str
    ):
        return UserAction(
            action=CommandType.load_file,
            datetime=str(datetime.now()),
            expired=False,
            success=success,
            reason=reason,
            payload={"filename": filename},
            user_name=user_name,
        )

    @classmethod
    async def run(
        cls,
        ws_response: WSResponse,
        meta: Meta,
        command: str = None,
        message_json: Dict[str, str] = None,
    ):
        if not command == CommandType.load_file:
            raise UnsuitableCommand

        key = message_json["key"]

        file = FileStore().get_file(key=key)

        if file:
            await NotificationStore().process(
                ws=ws_response,
                notification=LoadFileAction.get_load_file_notification(
                    user_name=meta.user_name,
                    filename=file.name,
                    success=True,
                    reason="",
                ),
            )

            await send_file(ws=ws_response, path=file.path)

            return meta

        await NotificationStore().process(
            ws=ws_response,
            notification=LoadFileAction.get_load_file_notification(
                user_name=meta.user_name,
                filename="",
                success=False,
                reason="Not allowed.",
            ),
        )
        return meta


class PublishFileAction(Command):
    @staticmethod
    def get_publish_file_notification(
        user_name: str, filename: str, key: str, success: str, reason: str
    ):
        return UserAction(
            action=CommandType.publish_file,
            datetime=str(datetime.now()),
            expired=False,
            success=success,
            reason=reason,
            payload={"filename": filename, "key": key},
            user_name=user_name,
        )

    @classmethod
    async def run(
        cls,
        ws_response: WSResponse,
        meta: Meta,
        command: str = None,
        message_json: Dict[str, str] = None,
    ):
        if not command == CommandType.publish_file:
            raise UnsuitableCommand

        try:
            filename = message_json["filename"]
        except KeyError:
            raise BadRequest

        file = await FileStore().publish_file(
            filename=filename, ws_response=ws_response
        )

        if file is not None:
            await NotificationStore().process(
                ws=ws_response,
                notification=PublishFileAction.get_publish_file_notification(
                    user_name=meta.user_name,
                    filename=filename,
                    key=file.key,
                    success=True,
                    reason="",
                ),
            )
            return meta

        await NotificationStore().process(
            ws=ws_response,
            notification=PublishFileAction.get_publish_file_notification(
                user_name=meta.user_name,
                filename=filename,
                key="",
                success=False,
                reason="Not allowed.",
            ),
        )

        return meta
