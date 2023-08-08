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

    # TODO:
    
    # Не получается использовать aprint()
    # Может чего-то не понимаю. Проблема следующая:
    # Если вызвать в event_loop сперва await ainput: он
    # начнет ожидать ввод из консоли; если во время ожидания
    # сработает await aprint, то, в консоль сообщение выведется,
    # после чего await ainput перестает откликаться.
    # https://github.com/vxgmichel/aioconsole/issues/47#issuecomment-464040281
    # тут не про это, но в целом о том, что могут быть проблемы...
