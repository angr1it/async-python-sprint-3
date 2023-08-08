from aioconsole import ainput

DEFAULT_PROMT = '<'


async def console_input(prompt: str = DEFAULT_PROMT):
    message_str = await ainput(prompt=prompt)
    try:
        str_command, content = message_str.split(" ", 1)
    except ValueError:
        str_command = message_str
        content = None

    return str_command, content


async def console_output(message):
    # await aprint(message)
    print(message)

    # Возмоно, вопрос ОС. попробовал поменять
    # версии образов сред, без изменений.
