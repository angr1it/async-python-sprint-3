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
    EmptyCommand,
    BadRequest,
    DialogueOpenedAlready,
    UnknownError,
    NoRegistredUserFound
)

from .state.meta import Meta
from .state.room import RoomStore, Room, RoomType
from .state.user import UserStore

from .command import Command


class LoadFileAction(Command):
    
    @classmethod
    async def run(cls, ws_response: web.WebSocketResponse, meta: Meta, command: str = None, message_json: Dict[str, str] = None):
 
        if not command == CommandType.join_room:
            raise UnsuitableCommand
        

        return meta
    
class PublishFileAction(Command):
    
    @classmethod
    async def run(cls, ws_response: web.WebSocketResponse, meta: Meta, command: str = None, message_json: Dict[str, str] = None):
 
        if not command == CommandType.join_room:
            raise UnsuitableCommand
        

        return meta