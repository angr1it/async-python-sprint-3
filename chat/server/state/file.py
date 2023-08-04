import logging
from aiohttp import web
from dataclasses import dataclass
import uuid
from typing import Dict

from ...singleton import singleton
from ...manage_files import receive_file

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class File:

    key: str
    path: str
    name: str



@singleton
class FileStore:
    
    def __init__(self) -> None:
        
        self.store: Dict[str, File] = {}

    def get_file(self, key: str) -> File:
        try:
            return self.store[key]
        except KeyError:
            return None
        
    async def publish_file(self, filename: str, ws_response: web.WebSocketResponse) -> File:
        
        key = str(uuid.uuid4())
        dir = './server_data/' + key

        success = await receive_file(ws=ws_response, dir=dir, filename=filename)
        if success:
            self.store[key] = File(key=key, path=f'{dir}/{filename}', name=filename)
            return self.store[key]

        return None
    
    async def load_file(self):
        pass