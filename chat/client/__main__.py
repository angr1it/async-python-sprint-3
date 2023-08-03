import asyncio
import logging
from typing import Coroutine

from aioconsole import ainput
from aiohttp import ClientSession, ClientWebSocketResponse
from aiohttp.http_websocket import WSMessage
from aiohttp.web import WSMsgType

from .client_commands import (
    HistoryCommand,
    SendCommand, 
    QuitCommand, 
    JoinRoomCommand,
    RegisterCommand,
    LoginCommand,
    LogoutCommand,
    PublishFile
)
from .client_commands import (
    CommandArgError, 
    EmptyCommand,
    UnsuitableCommand
)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('client')


async def subscribe_to_messages(websocket: ClientWebSocketResponse) -> None:
    """
    A subscription handler to subscribe to messages. Simply logs them. 
    
    :param websocket: Websocket connection
    :return: None, forever living task
    """
    async for message in websocket:
        if isinstance(message, WSMessage):
            if message.type == WSMsgType.text:
                logger.info('> Message from server received: %s', message.json())

async def ping(websocket: ClientWebSocketResponse) -> None:
    """
    A function that sends a PING every minute to keep the connection alive.

    Note that you can do this automatically by simply using `autoping=True` and `heartbeat`. 
    This is implemented as an example.
    
    :param websocket: Websocket connection
    :return: None, forever living task
    """
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
    commands = [SendCommand, HistoryCommand]

    while True:
        message = await input()

        try:
            str_command, content = message.split(' ', 1)
        except ValueError:
            str_command = message
            content = None

        processed = False
        for command in commands:
            try:
                await command.run(websocket, str_command, content)
                processed = True
            except UnsuitableCommand:
                continue
            except CommandArgError as ex:
                logger.error(ex)
            except EmptyCommand as ex:
                logger.error('Command is empty!')
                break
        
        if not processed:
            logger.info('Unknown command! Try again..')

async def handler(nick: str = None, room: str = None) -> None:
    """
    Does the following things well:
      * Task that subscribes to all messages from the server
      * Task that PINGs the backend every 60 second
      * Change the nickname to `Jonas`
      * Join a chat room called `test`
      * Allows sending message from the terminal
    Does the following bad:
      * Message formatting. Logs are simply written.
    :return: 
    """
    async with ClientSession() as session:
        async with session.ws_connect('ws://0.0.0.0:8080/chat', ssl=False) as ws:
            read_message_task = asyncio.create_task(subscribe_to_messages(websocket=ws))
            
            #await JoinRoom.run(ws, '/join_room', room)
            #await SetName.run(ws, '/set_name', nick)

            ping_task = asyncio.create_task(ping(websocket=ws))
            send_input_message_task = asyncio.create_task(handle_input(websocket=ws))

            #await UserList.run(ws, '/user_list')
            # This function returns two variables, a list of `done` and a list of `pending` tasks.
            # We can ask it to return when all tasks are completed, first task is completed or on first exception
            done, pending = await asyncio.wait(
                [read_message_task, ping_task, send_input_message_task], return_when=asyncio.FIRST_COMPLETED,
            )
            # When this line of line is hit, we know that one of the tasks has been completed.
            # In this program, this can happen when:
            #   * we (the client) or the server is closing the connection. (websocket.close() in aiohttp)
            #   * an exception is raised

            # First, we want to close the websocket connection if it's not closed by some other function above
            if not ws.closed:
                await ws.close()
            # Then, we cancel each task which is pending:
            for task in pending:
                task.cancel()
            # At this point, everything is shut down. The program will exit.


if __name__ == '__main__':
    #input_nick = input('Nick (random if not provided): ')
    #input_room = input('Room (`Default` if not provided): ')
    asyncio.run(handler(nick='', room=''))