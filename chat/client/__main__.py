import asyncio
import logging


from chat.utils.my_response import WSResponse
from chat.client.client_commands import CommandArgError, EmptyCommand
from chat.command_types import CommandType
from chat.manage_files import receive_file
from chat.client.get_commands import init_commands
from chat.client.console import console_input, console_output


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(message)s", datefmt="%d-%b-%y %H:%M:%S"
)
logger = logging.getLogger("client")

DOWNLOADS_FOLDER = "./client_data/downloads"


async def subscribe_to_messages(websocket: WSResponse) -> None:
    while True:
        data = await websocket.receive_json()
        await console_output(data)

        try:
            if data["action"] == CommandType.load_file and data["success"]:
                await receive_file(
                    ws=websocket,
                    dir=DOWNLOADS_FOLDER,
                    filename=data["payload"]["filename"],
                )

                logger.info("Loaded.")

        except KeyError as ex:
            logger.error(ex)
        # TODO:
        # except Exception as ex:
        #     logger.error(ex)
        #     logger.info("File was lost somehow...")


async def handle_input(websocket: WSResponse) -> None:
    commands = init_commands()

    while True:
        command, content = await console_input()

        try:
            await commands[CommandType(command)].run(
                ws=websocket, command=command, content=content
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


async def main():
    ws = await init_connection()
    tasks = [
        subscribe_to_messages(websocket=ws),
        handle_input(websocket=ws),
    ]
    try:
        await asyncio.gather(*tasks)
    except asyncio.CancelledError:
        ws.close()
        pass

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        # Инче отображает trace, но без ошибки:
        # ERROR:asyncio:Task was destroyed but it is pending!...
        print("Exiting...")
