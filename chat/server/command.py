from typing import Dict
import logging
from aiohttp import web

from .state.meta import Meta


logger = logging.getLogger()

class Command:
    @classmethod
    async def run(cls, ws_response: web.WebSocketResponse, meta: Meta, command: str = None, message_json: Dict[str, str] = None) -> Meta:
        pass



    

