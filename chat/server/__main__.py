import logging
import uuid
import asyncio
from asyncio import StreamReader, StreamWriter
from ..utils.my_response import WSResponse

from .state.meta import Meta
from .state.user import (
    UserStore
)
from .state.message import (
    NotificationStore,
    get_connected_notification,
    get_error_message
)
from .state.room import RoomStore

from ..exceptions import (
    BadRequest,
    NoRegistredUserFound
)
from .get_commands import init_commands

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('server')


async def handle_client(reader: StreamReader, writer: StreamWriter):
    
    username = UserStore().get_anonymus_name()
    meta = Meta(uuid.uuid5, username, False)

    websocket = WSResponse(reader=reader, writer=writer)
    
    await NotificationStore().process(
        ws=websocket,
        notification=get_connected_notification(meta.user_name)
    )
    
    commads = init_commands()
    
    while True:
        message = await websocket.receive_json()
        command_str = message.get('command')
        
        try:
            meta = await commads[command_str].run(
                ws_response=websocket,
                meta=meta,
                command=command_str,
                message_json=message
            )
        except BadRequest:
            await NotificationStore().process(
                ws=websocket, 
                notification=get_error_message(reason='Bad request.')
            )
        except NoRegistredUserFound:
            await NotificationStore().process(
                ws=websocket,
                notification=get_error_message(reason='Cannot apply this operation to anonymus user.')
            )
        except:
            await NotificationStore().process(
                ws=websocket,
                notification=get_error_message(reason='Unknown error.')
            )


async def init_app(host, port):
    await UserStore().load()
    await RoomStore().load()
    await NotificationStore().load()

    server = await asyncio.start_server(handle_client, host, port)
    
    async with server:
        await server.serve_forever()

async def shutdown():
    logger.info('Shutting down server...')
    await UserStore().dump()
    await RoomStore().dump()
    await NotificationStore().dump()


HOST, PORT = "", 8000

if __name__ == '__main__':
    try:
        asyncio.run(init_app(HOST, PORT))
    except KeyboardInterrupt:
        asyncio.run(shutdown())