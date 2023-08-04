import asyncio
import logging
from typing import Coroutine

from aioconsole import ainput
from aiohttp import ClientSession, ClientWebSocketResponse
from aiohttp.http_websocket import WSMessage
from aiohttp.web import WSMsgType


from .client_commands import (
    CommandArgError, 
    EmptyCommand,
)
from ..command_types import CommandType
from ..manage_files import receive_file

from .get_commands import init_commands

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('client')

DOWNLOADS_FOLDER = './client_data/downloads'

async def subscribe_to_messages(websocket: ClientWebSocketResponse) -> None:
    """
    A subscription handler to subscribe to messages. Simply logs them. 
    
    :param websocket: Websocket connection
    :return: None, forever living task
    """
    async for message in websocket:
        if isinstance(message, WSMessage):
            if message.type == WSMsgType.text:
                data = message.json()
                logger.info('> Message: %s', data)

                try:
                    if data['action'] == CommandType.load_file and data['success']:
                        await receive_file(ws=websocket, dir=DOWNLOADS_FOLDER, filename=data['payload']['filename'])

                        logger.info('Loaded.')

                except Exception as ex:
                    logger.error(ex)
                    logger.info('File was lost somehow...')

async def ping(websocket: ClientWebSocketResponse) -> None:

    while True:
        logger.debug('< PING')
        await websocket.ping()
        await asyncio.sleep(60)

async def console_input() -> Coroutine[str, str, str]:
    return await ainput('<<<')

async def handle_input(websocket: ClientWebSocketResponse, input: Coroutine[str, str, str] = console_input) -> None:
    """
    Reads input from input-coroutine and chooses which request send to server;

    :param websocket: Websocket connection
    :param input: Coroutine that handles inputs -- yields str
    :return:
    """
    commands = init_commands()

    while True:
        message = await input()

        try:
            str_command, content = message.split(' ', 1)
        except ValueError:
            str_command = message
            content = None

        try:
            await commands[CommandType(str_command)].run(websocket, str_command, content)
        except CommandArgError as ex:
            logger.error(ex)
        except EmptyCommand as ex:
            logger.error('Command is empty!')
        except ValueError:
            logger.info('Wrong command! Look for /help!')
        

async def handler(nick: str = None, room: str = None) -> None:

    async with ClientSession() as session:
        async with session.ws_connect('ws://0.0.0.0:8080/chat', ssl=False) as ws:
            read_message_task = asyncio.create_task(subscribe_to_messages(websocket=ws))
            
            ping_task = asyncio.create_task(ping(websocket=ws))
            send_input_message_task = asyncio.create_task(handle_input(websocket=ws))


            done, pending = await asyncio.wait(
                [read_message_task, ping_task, send_input_message_task], return_when=asyncio.FIRST_COMPLETED,
            )

            if not ws.closed:
                await ws.close()

            for task in pending:
                task.cancel()

if __name__ == '__main__':
    asyncio.run(handler(nick='', room=''))