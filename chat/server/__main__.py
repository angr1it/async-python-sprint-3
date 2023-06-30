import logging
import random
from collections import defaultdict

from aiohttp import web
from aiohttp.http_websocket import WSCloseCode, WSMessage
from aiohttp.web_request import Request

from .utils import broadcast, get_anonymous_nick
from .server_actions import (
    History,
    JoinRoom,
    UserList,
    Send,
    Register,
    Login,
    Logout
)
from ..exceptions import *
from .actions import ActionMessages
from .meta import Meta


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

    room = 'Global'

    user = get_anonymous_nick()
    logger.info('%s connected to room %s', user, room)

    await current_websocket.send_json(ActionMessages.connecting(user, room))

    # Check that the user does not exist in the room already
    # if request.app['websockets'][room].get(user):
    #     logger.warning('User already connected. Disconnecting.')
    #     await current_websocket.close(code=WSCloseCode.TRY_AGAIN_LATER, message=b'Username already in use')
    #     return current_websocket
    # else:

    request.app['websockets'][room][user] = current_websocket
    
    for ws in request.app['websockets'][room].values():
        await ws.send_json(ActionMessages.join_room(username=user, room=room, success=True, message=''))

    commands = [JoinRoom, UserList, Send, History, Register, Login, Logout]

    meta = Meta(user, room, False)

    try:
        async for message in current_websocket:
            if isinstance(message, WSMessage):
                if message.type == web.WSMsgType.text:
                    
                    message_json = message.json()
                    command_str = message_json.get('command')
                    
                    for command in commands:
                        try:
                            meta = await command.run(request = request, ws_response = current_websocket, meta = meta, command = command_str, message_json = message_json)
                        except UnsuitableCommand:
                            continue
    
    finally:
        request.app['websockets'][room].pop(user)
    
    if current_websocket.closed:
        await broadcast(
            app=request.app, room=room, message=ActionMessages.left_room(user, room, False)
        )
    else:
        await broadcast(
            app=request.app, room=room, message=ActionMessages.left_room(user, room, True)
        )
    return current_websocket


async def init_app() -> web.Application:
    """
    Creates an backend app object with a 'websockets' dict on it, where we can store open websocket connections.
    :return: The app
    """
    app = web.Application()
    app['websockets'] = defaultdict(dict)

    app.on_shutdown.append(shutdown)  # Shut down connections before shutting down the app entirely
    app.add_routes([web.get('/echo', handler=ws_echo)])  # `ws_echo` handles this request.
    app.add_routes([web.get('/chat', handler=ws_chat)])  # `ws_chat` handles this request

    return app


async def shutdown(app):
    for room in app['websockets']:
        for ws in app['websockets'][room].values():
            ws.close()
    app['websockets'].clear()


if __name__ == '__main__':
    web.run_app(init_app())