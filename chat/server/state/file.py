import logging
from dataclasses import dataclass
import uuid

from chat.singleton import singleton
from chat.manage_files import receive_file
from chat.utils.my_response import WSResponse


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


@dataclass
class File:
    key: str
    path: str
    name: str


@singleton
class FileStore:
    def __init__(self) -> None:
        self.store: dict[str, File] = {}

    def get_file(self, key: str) -> File:
        try:
            return self.store[key]
        except KeyError:
            return None

    async def publish_file(
        self, filename: str, ws_response: WSResponse
    ) -> File:
        key = str(uuid.uuid4())
        dir = "./server_data/" + key

        success = await receive_file(
            ws=ws_response, dir=dir, filename=filename
        )
        if success:
            self.store[key] = File(
                key=key, path=f"{dir}/{filename}", name=filename
            )
            return self.store[key]

        return None
