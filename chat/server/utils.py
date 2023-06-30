import logging
from typing import Dict, List, Tuple, Union
import json
from aiohttp import web
import dataclasses
import random
from .message import Message

from .actions import ActionMessages

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
  

def get_anonymous_nick(max_n: int = 1000000):
    return f'anonymous{random.randint(0, max_n)}'

async def change_nick(
    app: web.Application, room: str, new_nick: str, old_nick: str
) -> Tuple[Dict[str, Union[str, bool]], bool]:
    """
    Takes a user and changes it's nickname.
    :param app: Application
    :param room: Room the user is in
    :param new_nick: New nick
    :param old_nick: Old nick
    :return: A tuple that contains the dict to be returned to the end user and whether it was successful or not.
    """
    if not isinstance(new_nick, str) or not 3 <= len(new_nick) <= 20:
        return (
            {'action': 'set_nick', 'success': False, 'message': 'Name must be a string and between 3-20 chars.'},
            False,
        )
    if new_nick in app['websockets'][room].keys():
        return (
            {'action': 'set_nick', 'success': False, 'message': 'Name already in use.'},
            False,
        )
    else:
        app['websockets'][room][new_nick] = app['websockets'][room].pop(old_nick)
        return {'action': 'set_nick', 'success': True, 'message': ''}, True


async def broadcast(app: web.Application, room: str, message: dict, ignore_user: str = None) -> None:
    """
    Broadcasts a message to every user in a room. Can specify a user to ignore. 

    :param app: Application. From a request, pass `request.app`
    :param room: Room name
    :param message: What to broadcast
    :param ignore_user: Skip broadcast to this user (used for e.g. chat messages)
    :return: None
    """
    for user, ws in app['websockets'][room].items():
        if ignore_user and user == ignore_user:
            pass
        else:
            logger.info('> Sending message %s to %s', message, user)
            await ws.send_json(message)

async def send_to_client(app: web.Application, room: str, message: dict, user: str) -> None:
    """
    Sends a message to a specified user.

    :param app: Application. From a request, pass `request.app`;
    :param room: Room name;
    :param message: What to broadcast;
    :param user: User to send a message. Assumed, that user is inside of spec   ified `room`, else RuntimeError;
    :return: None
    """
    if not user in app['websockets'][room].keys():
        raise RuntimeError(f'There is no {user} in {room}')
    
    await app['websockets'][room][user].send_json(message)