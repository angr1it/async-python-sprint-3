from asyncio import StreamReader, StreamWriter
import json

CHUNK_SIZE = 1024
END_SIGNAL = b"10101101110111110"


class WSResponse:
    def __init__(
        self,
        reader: StreamReader,
        writer: StreamWriter,
        chunk_size: int = CHUNK_SIZE,
        end_signal: bytes = END_SIGNAL,
    ) -> None:
        self.reader = reader
        self.writer = writer
        self.end_signal = end_signal
        self.chunk_size = chunk_size

    async def receive_bytes(self):
        data: bytes = b""

        while True:
            chunk = await self.reader.read(
                self.chunk_size + len(self.end_signal)
            )
            data += chunk

            if data[-1 * len(self.end_signal):] == self.end_signal:
                return data[: -1 * len(self.end_signal)]

    async def receive_json(self):
        return json.loads(await self.receive_bytes())

    async def send_bytes(self, data: bytes):

        for i in range(0, int(len(data) / self.chunk_size) + 1):
            self.writer.write(
                data[i * self.chunk_size: (i + 1) * self.chunk_size]
            )
            await self.writer.drain()

        self.writer.write(self.end_signal)
        await self.writer.drain()

    async def send_json(self, data: dict):
        bdata = json.dumps(data).encode("utf-8")
        await self.send_bytes(bdata)

    async def close(self):
        self.writer.close()
        await self.writer.wait_closed()
