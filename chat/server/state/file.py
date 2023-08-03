from dataclasses import dataclass
import dataclasses
import json
from typing import List
import logging
import asyncio
from datetime import datetime
from aiohttp import web

import uuid
import aiofiles

from ...singleton import singleton
from ...command_types import CommandType
from .message import NotificationStore, FileLoaded, FilePublished

from ...utils import send_to_client, broadcast

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from dataclasses import dataclass
from abc import ABC, abstractmethod



@singleton
class FileStore:

    @staticmethod
    async def __receive_file(ws: web.WebSocketResponse, dir: str, filename: str, timeout: float = 0.1):
        await aiofiles.os.makedirs(dir, exist_ok=True)
        async with aiofiles.open(dir + '/' + filename, 'wb') as f:
            while True:
                chunk = await ws.receive_bytes(timeout=timeout)

                while isinstance(chunk, bytes):
                    await f.write(chunk)
                    try:
                        chunk = await ws.receive_bytes(timeout=timeout)

                    except asyncio.exceptions.TimeoutError:
                        logger.info(f'File saved {dir}/{filename}')
                        return
        
    async def publish_file(self, filename: str, ws_response: web.WebSocketResponse, app: web.Application) -> bool:
        
        key = str(uuid.uuid4())
        dir = './server_data/' + key

        success = await FileStore.__receive_file(ws=ws_response, dir=dir, filename=filename)
        if success:
            NotificationStore().process(
                app=app,
                notification=FileLoaded(CommandType.publish_file, datetime.now(), True, '')
            )

            return True
        
        NotificationStore().process(
            app=app,
            notification=FileLoaded(CommandType.publish_file, datetime.now(), False, 'Unknown.')
        )

        return False
    
    async def load_file(self):
        pass