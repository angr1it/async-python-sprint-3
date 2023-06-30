from enum import Enum


class CommandType(str, Enum):
    send = '/send'
    send_to = '/send_to'
    quit = '/quit'
    join_room = '/join_room'
    set_name = '/set_name'
    user_list = '/user_list'
    register = '/register'
    login = '/login'
    logout = '/logout'
    history = '/history'