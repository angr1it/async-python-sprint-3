from typing import List, Dict, Tuple, Union
from aiohttp import ClientWebSocketResponse
import logging
from datetime import datetime
import dataclasses
from aiohttp import web
from aiohttp.web_request import Request
import aiofiles
from datetime import datetime
import asyncio
import json

import uuid

logger = logging.getLogger()

from ..command_types import CommandType


from ..exceptions import (
    UnsuitableCommand,
    CommandArgError,
    EmptyCommand
)

from .state.meta import Meta
from .state.room import RoomStore
from .state.user import UserStore
from .state.message import NotificationStore, Message


class Command:
    @classmethod
    async def run(cls, ws_response: web.WebSocketResponse, meta: Meta, command: str = None, message_json: Dict[str, str] = None) -> Meta:
        pass
