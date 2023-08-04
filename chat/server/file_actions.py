from typing import Dict
import logging
from aiohttp import web
from datetime import datetime


from ..command_types import CommandType
from ..exceptions import (
    UnsuitableCommand,
    BadRequest,
)
from .state.meta import Meta
from .state.message import NotificationStore, UserAction
from .state.file import FileStore
from .command import Command
from ..manage_files import send_file

logger = logging.getLogger()


class LoadFileAction(Command):
    
    @staticmethod
    def get_load_file_notification(user_name: str, filename: str, success: str, reason: str):
        return UserAction(
            action=CommandType.load_file,
            datetime=str(datetime.now()),
            expired=False,
            success=success,
            reason=reason,
            payload={
                'filename': filename
            },
            user_name=user_name
        )
    
    @classmethod
    async def run(cls, ws_response: web.WebSocketResponse, meta: Meta, command: str = None, message_json: Dict[str, str] = None):
 
        if not command == CommandType.load_file:
            raise UnsuitableCommand
        
        key = message_json['key']

        file = FileStore().get_file(key=key)

        if not file is None:
            
            await NotificationStore().process(
                ws=ws_response,
                notification=LoadFileAction.get_load_file_notification(user_name=meta.user_name, filename=file.name, success=True, reason='')
            )

            await send_file(ws=ws_response, path=file.path)

            return meta

        await NotificationStore().process(
            ws=ws_response,
            notification=LoadFileAction.get_load_file_notification(user_name=meta.user_name, filename='', success=False, reason='Not allowed.')
        )
        return meta
    
class PublishFileAction(Command):
    
    @staticmethod
    def get_publish_file_notification(user_name: str, filename: str, key: str, success: str, reason: str):
        return UserAction(
            action=CommandType.publish_file,
            datetime=str(datetime.now()),
            expired=False,
            success=success,
            reason=reason,
            payload={
                'filename': filename,
                'key': key
            },
            user_name=user_name
        )

    @classmethod
    async def run(cls, ws_response: web.WebSocketResponse, meta: Meta, command: str = None, message_json: Dict[str, str] = None):
 
        if not command == CommandType.publish_file:
            raise UnsuitableCommand
        
        try:
            filename = message_json['filename']
        except:
            raise BadRequest
        
        file = await FileStore().publish_file(filename=filename, ws_response=ws_response)

        if not file is None:
            await NotificationStore().process(
                ws=ws_response,
                notification=PublishFileAction.get_publish_file_notification(user_name=meta.user_name, filename=filename, key=file.key, success=True, reason='')
            )
            return meta
        
        await NotificationStore().process(
            ws=ws_response,
            notification=PublishFileAction.get_publish_file_notification(user_name=meta.user_name, filename=filename, key='', success=False, reason='Not allowed.')
        )

        return meta