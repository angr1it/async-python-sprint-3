import logging
import random
from collections import defaultdict
import asyncio
from datetime import datetime
from aiohttp import web
from aiohttp.http_websocket import WSCloseCode, WSMessage
from aiohttp.web_request import Request
import uuid

from .room_actions import (
    JoinRoomAction,
    LeaveRoomAction,
    CreateRoomAction,
    DeleteRoomAction,
    AddUserAction,
    RemoveUserAction
)
from .user_actions import (
    RegisterAction,
    LoginAction,
    LogoutAction
)
from .message_actions import (
    SendAction,
    HistoryAction,
)

from .state.meta import Meta
from .state.user import (
    UserStore
)
from .state.message import (
    NotificationStore,
    ConnectAnon,
    AnyError
)

from ..exceptions import *
from ..command_types import CommandType
from .get_commands import init_commands

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def ws_echo(request: Request) -> web.WebSocketResponse:
    """
    Echo service to send back the JSON sent to this endpoint, but wrapped in {'echo': <input>}

    :param request: Request object
    :return: The websocket response
    """
    websocket = web.WebSocketResponse()

    ready = websocket.can_prepare(request=request)
    if not ready:
        await websocket.close(code=WSCloseCode.PROTOCOL_ERROR)

    await websocket.prepare(request)

    async for message in websocket:
        if isinstance(message, WSMessage):
            if message.type == web.WSMsgType.text:
                message_json = message.json()
                logger.info('> Received: %s', message_json)
                echo = {'echo': message_json}
                await websocket.send_json(echo)
                logger.info('< Sent: %s', echo)

    return websocket

async def ws_chat(request: Request) -> web.WebSocketResponse:
    """
    Chat backend. Add it to the route like this:
        - app.add_routes([web.get('/chat', handler=ws_chat)])

    :param request: Request object
    :return: Websocket response
    """
    current_websocket = web.WebSocketResponse(autoping=True, heartbeat=60)

    ready = current_websocket.can_prepare(request=request)
    if not ready:
        await current_websocket.close(code=WSCloseCode.PROTOCOL_ERROR)
    await current_websocket.prepare(request)

    username = UserStore().get_anonymus_name()
    meta = Meta(uuid.uuid5, username, False)

    await NotificationStore().process(
        ws=current_websocket,
        notification=ConnectAnon(
            action=CommandType.connected,
            datetime=datetime.now(),
            success=True,
            reason='',
            name=meta.user_name,
            expired=False
        )
    )

    request.app['websockets'][meta.key] = current_websocket

    commands = init_commands()

    try:
        async for message in current_websocket:
            if isinstance(message, WSMessage):
                if message.type == web.WSMsgType.text:
                    
                    try:
                        message_json = message.json()
                        command_str = message_json.get('command')
                    
                        meta = await commands[command_str].run(ws_response = current_websocket, meta = meta, command = command_str, message_json = message_json)
                    except BadRequest:
                        await NotificationStore().process(
                            ws=current_websocket, 
                            notification=AnyError(CommandType.error, datetime.now(), expired=False, success=False, reason='Bad request.')
                        )
                    except NoRegistredUserFound:
                        await NotificationStore().process(
                            ws=current_websocket, 
                            notification=AnyError(CommandType.error, datetime.now(), expired=False, success=False, reason='Cannot apply this operation to anonymus user.')
                        )
                    except:
                        await NotificationStore().process(
                            ws=current_websocket, 
                            notification=AnyError(CommandType.error, datetime.now(), expired=False, success=False, reason='Unknown error.')
                        )
    
    finally:
        request.app['websockets'].pop(meta.key)
    
    return current_websocket

async def init_app() -> web.Application:
    """
    Creates an backend app object with a 'websockets' dict on it, where we can store open websocket connections.
    :return: The app
    """
    app = web.Application()
    app['websockets'] = defaultdict(dict)

    await NotificationStore().load()
    await UserStore().load()

    app.on_shutdown.append(shutdown)
    app.add_routes([web.get('/echo', handler=ws_echo)])
    app.add_routes([web.get('/chat', handler=ws_chat)])  
    app.update()
    return app

async def shutdown(app):
    # CTRL+C in order to save the data on app close
    await NotificationStore().dump()
    await UserStore().dump()

    for room in app['websockets']:
        for ws in app['websockets'][room].values():
            ws.close()
    app['websockets'].clear()


if __name__ == '__main__':
    web.run_app(init_app())