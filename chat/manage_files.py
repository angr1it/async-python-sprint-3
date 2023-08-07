from pathlib import Path
import aiofiles
from aiofiles.os import makedirs
from pathlib import Path
import json
import dataclasses
import logging

from chat.utils.my_response import WSResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BytesEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, bytes):
            return obj.decode('utf-8')
        return json.JSONEncoder.default(self, obj)


async def write_file(filepath: str, data: str):
    dir = str(Path(filepath).parent)
    await makedirs(dir, exist_ok=True)
    async with aiofiles.open(file=filepath, mode="w") as f:
        await f.write(data)


async def read_file(filepath) -> dict:
    async with aiofiles.open(file=filepath, mode="r") as f:
        data = await f.read()

    return json.loads(data)


def to_dict(data: dict[str, dataclasses.dataclass]):
    out = dict()
    for key, value in data.items():
        out[key] = json.dumps(
            dataclasses.asdict(value), indent=4, cls=BytesEncoder
        )

    return out


async def receive_file(ws: WSResponse, dir: str, filename: str):
    await aiofiles.os.makedirs(dir, exist_ok=True)
    async with aiofiles.open(dir + "/" + filename, "wb") as f:
        chunk = await ws.receive_bytes()
        await f.write(chunk)

        return True


async def send_file(ws: WSResponse, path: str):
    async with aiofiles.open(path, "rb") as f:
        chunk = await f.read(2**16)
        await ws.send_bytes(chunk)
