from pathlib import Path
import aiofiles
from aiofiles.os import makedirs
from pathlib import Path
import json
from typing import Dict

async def write_file(filepath: str, data: str):
    dir = str(Path(filepath).parent)
    await makedirs(dir, exist_ok=True)
    async with aiofiles.open(file=filepath, mode='w') as f:
        await f.write(data)

async def read_file(filepath) -> Dict:
    
    async with aiofiles.open(file=filepath, mode='r') as f:
        data = await f.read()

    return json.loads(data)