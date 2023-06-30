import unittest
from aiohttp.test_utils import AioHTTPTestCase
from aiohttp import web
from collections import defaultdict
from typing import Coroutine, Any

from aiohttp.web import Application


from chat.client.client_commands import (
    SendCommand, 
    QuitCommand, 
    JoinRoom, 
    SetName,
    UserList
)
from chat.client.client_commands import (
    CommandArgError, 
    EmptyCommand,
    UnsuitableCommand
)




class TestClientCommands(AioHTTPTestCase):
    async def get_application(self) -> Coroutine[Any, Any, Application]:
        return await super().get_application()
    
    async def test_SendCommand(self):
        async with self.client.session.ws_connect() as ws:
            res = await SendCommand.run(ws, '/send', 'hello')

        self.assertIn("Hello, world", res)

if __name__ == '__main__':
    unittest.main()