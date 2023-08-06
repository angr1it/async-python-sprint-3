from pathlib import Path
import aiofiles
from aiofiles.os import makedirs
from pathlib import Path
import json
from typing import Dict
import dataclasses
import logging

from chat.utils.my_response import WSResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def write_file(filepath: str, data: str):
    dir = str(Path(filepath).parent)
    await makedirs(dir, exist_ok=True)
    async with aiofiles.open(file=filepath, mode="w") as f:
        await f.write(data)


async def read_file(filepath) -> Dict:
    async with aiofiles.open(file=filepath, mode="r") as f:
        data = await f.read()

    return json.loads(data)


def to_dict(data: Dict[str, dataclasses.dataclass]):
    out = dict()
    for key, value in data.items():
        out[key] = json.dumps(dataclasses.asdict(value), indent=4)

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
