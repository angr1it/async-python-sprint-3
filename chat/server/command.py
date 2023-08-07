import logging

from .state.meta import Meta
from ..utils.my_response import WSResponse

logger = logging.getLogger()


class Command:
    @classmethod
    async def run(
        cls,
        ws_response: WSResponse,
        meta: Meta,
        command: str = None,
        message_json: dict[str, str] = None,
    ) -> Meta:
        pass
