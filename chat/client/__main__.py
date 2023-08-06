import asyncio
import logging
from typing import Coroutine
from aioconsole import ainput
import asyncio

from chat.utils.my_response import WSResponse

from chat.client.client_commands import CommandArgError, EmptyCommand

from chat.command_types import CommandType
from chat.manage_files import receive_file
from chat.client.get_commands import init_commands

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S"
)
logger = logging.getLogger("client")

DOWNLOADS_FOLDER = "./client_data/downloads"


async def subscribe_to_messages(websocket: WSResponse) -> None:
    while True:
        data = await websocket.receive_json()
        logger.info("> Message: %s", data)

        try:
            if data["action"] == CommandType.load_file and data["success"]:
                await receive_file(
                    ws=websocket,
                    dir=DOWNLOADS_FOLDER,
                    filename=data["payload"]["filename"],
                )

                logger.info("Loaded.")

        except Exception as ex:
            logger.error(ex)
            logger.info("File was lost somehow...")


async def ping(websocket) -> None:
    while True:
        logger.debug("< PING")
        await websocket.ping()
        await asyncio.sleep(60)


async def console_input() -> Coroutine[str, str, str]:
    return await ainput("<<<")


async def handle_input(
    websocket: WSResponse, input: Coroutine[str, str, str] = console_input
) -> None:
    commands = init_commands()

    while True:
        message = await input()
        try:
            str_command, content = message.split(" ", 1)
        except ValueError:
            str_command = message
            content = None

        try:
            await commands[CommandType(str_command)].run(
                ws=websocket, command=str_command, content=content
            )
        except CommandArgError as ex:
            logger.error(ex)
        except EmptyCommand:
            logger.error("Command is empty!")
        except ValueError:
            logger.info("Wrong command! Look for /help!")


async def init_connection():
    reader, writer = await asyncio.open_connection("127.0.0.1", 8000)

    return WSResponse(reader=reader, writer=writer)


if __name__ == "__main__":
    loop = asyncio.new_event_loop()

    ws = loop.run_until_complete(init_connection())

    tasks = [
        loop.create_task(handle_input(websocket=ws)),
        loop.create_task(subscribe_to_messages(websocket=ws)),
    ]

    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()
