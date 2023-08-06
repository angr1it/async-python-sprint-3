from enum import Enum
DOC = f"""
    Commands: 

    -- Commands/arguments separated by one space; <> - required, [] -optional

    `/send <room_name> <message>` : sends a public message visible inside of current room;

    `/send_private <username> <message>`: sends a private message to a specified username; need to /open_dialogue before using this;
    
    `/history [n] [room_name]` : returns last n messages available inside of current room; n = 20 by default; if no room_name passed -- returns user's action history if loggedin.

    `/create_room <room_name> <room_type := (/open or /restricted)>` : creates a room with current user as admin (need to be logged in);

    `/delete_room <room_name>` : deletes the room if current user is admin;

    `/add_user <room_name> <user_name>` : adds user to allowed list (for /restricted room); this user needs to be registred; for admins;

    `/remove_user <room_name> <user_name>` : removes user from the room and allowed list; for admins;

    `/join_room <room_name>` : attemps to join specified room; /open -- opened for all; /restricted -- allowed list;

    `/leave_room <room_name>` : leaves the room;

    `/open_dialogue <user_name>` : tryes to open private chat with user;

    `/delete_dialogue <user_name>` : deletes private chat with user;

    `/register <username> <password>` : registers (username, password) combination;

    `/login <username> <password>` : attemps to login under specified (username, password) combination;

    `/logout` : logs out current user;

    `/quit` : quits application;

    `/publish_file <path>` : uploads file to server;

    `/load_file <key>` : tries to load a file with specified key;

    `/help` : returns this doc.
    
    """

class CommandType(str, Enum):  
    
    send = '/send'
    send_private = '/send_private'
    
    history = '/history'

    create_room = '/create_room'
    delete_room = '/delete_room'

    add_user = '/add_user'
    remove_user = '/remove_user'

    join_room = '/join_room'
    leave_room = '/leave_room'

    open_dialogue = '/open_dialogue'
    delete_dialogue = '/delete_dialogue'

    register = '/register'
    login = '/login'
    logout = '/logout'
    

    publish_file = '/publish_file'
    load_file = '/load_file'

    help = '/help'

    connected = '/connected'
    error = '/error'

    quit = '/quit'

CommandType.__doc__ = DOC
