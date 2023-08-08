import logging

import asyncio
from asyncio import StreamReader, StreamWriter

from chat.utils.my_response import WSResponse
from chat.server.get_commands import init_commands
from chat.server.state.meta import Meta
from chat.server.state.user import UserStore
from chat.server.state.message import (
    NotificationStore,
    get_connected_notification,
    get_error_message,
)
from chat.server.state.room import RoomStore
from chat.exceptions import (
    BadRequest,
    NoRegistredUserFound,
    CloseSession
)
from chat.server.user_actions import LogoutAction
from chat.command_types import CommandType

logging.basicConfig(
    filename="server.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
)
logger = logging.getLogger("server")

NO_REGISTRED_FOUND = "Cannot apply this operation to anonymus user."
BAD_REQUEST = "Bad request."

HOST, PORT = "", 8000

sockets: list[WSResponse] = []


def log_requests(request: dict, username: str) -> None:
    exclude = ['password']

    logger.info(
        f'{username}: %s',
        {x: request[x] for x in request if x not in exclude}
    )


async def close_session(ws: WSResponse, user_name: str):
    try:
        sockets.remove(ws)
        await NotificationStore().process(
            ws=ws,
            notification=LogoutAction.get_logout(
                success=True,
                reason='',
                user_name=user_name
            )
        )
        logger.info(f'Closing session with username:{user_name}')
        await ws.close()
    except ConnectionResetError:
        pass


async def handle_client(reader: StreamReader, writer: StreamWriter):
    user_name = UserStore().get_anonymus_name()
    logger.info(f'Opening session with username:{user_name}')
    meta = Meta(user_name, False)

    websocket = WSResponse(reader=reader, writer=writer)

    sockets.append(websocket)

    await NotificationStore().process(
        ws=websocket, notification=get_connected_notification(
            meta.user_name
        ))

    commads = init_commands()

    while True:
        message = await websocket.receive_json()
        log_requests(message, meta.user_name)

        command_str = message.get("command")

        try:

            meta = await commads[command_str].run(
                ws_response=websocket,
                meta=meta,
                command=command_str,
                message_json=message,
            )

        except BadRequest:
            await NotificationStore().process(
                ws=websocket, notification=get_error_message(
                    reason=BAD_REQUEST
                ))
        except NoRegistredUserFound:
            await NotificationStore().process(
                ws=websocket, notification=get_error_message(
                    reason=NO_REGISTRED_FOUND
                ))
        except (CloseSession, ConnectionResetError):
            await close_session(ws=websocket, user_name=meta.user_name)
            return


async def init_app(host, port):

    await UserStore().load()
    await RoomStore().load()
    await NotificationStore().load()

    logger.info("Server started. Ctrl+C to shutdown (to save state).")
    server = await asyncio.start_server(handle_client, host, port)

    async with server:
        try:
            await server.serve_forever()
        except asyncio.CancelledError:

            logger.info('Shutting...')
            [await notify_server_quit(ws) for ws in sockets]
            [await ws.close() for ws in sockets]

            server.close()
            await shutdown()


async def notify_server_quit(ws: WSResponse):
    await ws.send_json({'action': CommandType.quit})


async def shutdown():

    tasks = asyncio.all_tasks()
    tasks.remove(asyncio.current_task())
    [task.cancel() for task in tasks]
    [await task for task in tasks]

    await UserStore().dump()
    await RoomStore().dump()
    await NotificationStore().dump()


if __name__ == "__main__":
    try:
        asyncio.run(init_app(HOST, PORT))
    except (KeyboardInterrupt):
        logger.info('Server stopped.')
