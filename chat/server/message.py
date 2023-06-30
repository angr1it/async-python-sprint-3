from dataclasses import dataclass
from typing import List
import logging

from ..singleton import singleton

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Message:

    from_user: str
    to: str
    private: bool
    room: str
    message_str: str
    datetime: float


@singleton
class MessageStore:

    def __init__(self) -> None:
        self.store = {}

    def add(self, room:str, message: Message):

        try:
            self.store[room].append(message)
        except KeyError:
            self.store[room]: List[Message] = []
            self.store[room].append(message)

        logger.info('%s: Message from %s to %s: %s -- saved', room, message.from_user, message.to, message.message_str)

    def get_n_messages(self, room: str, n: int) -> List[Message]:
        if n < 1:
            logger.error(f'MessageStore: get_n_messages with n eq {n} < 1. Set to default eq 20.')
            n = 20
        
        try:
            return self.store[room][:n]
        except KeyError:
            logger.info(f'MessageStore: there is no messages in room {room}')
            return None

    def dump(self, path):
        pass

    def load(self, path):
        pass
        
