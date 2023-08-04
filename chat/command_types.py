from enum import Enum


class CommandType(str, Enum):
      
    """
    Commands: 
    TODO: NEED TO UPDATE

    -- Commands/arguments separated by one space;

    `/send <message>` : sends a public message visible inside of current room;

    `/send_to <username> <message>`: sends a private message to a specified username;

    `/quit` : quits application;

    `/join_room <room>` : attemps to join specified room;

    `/register` : returns user list for current room;

    `/register <username> <key>` : registers (username, key) combination;

    `/login <username> <key>` : attemps to login under specified (username, key) combination;

    `/logout` : logs out current user;

    `/history [n]` : returns last n messages available inside of current room; n = 20 by default;

    `/publish_file <path> [username1] [username2] ... [usernamen]` : uploads file to server; notifies users if specified; returns has-key to load it;

    `/load_file <hash-key>` : tries to load a file with specified hash-key;

    `/help` : returns this doc.
    
    """
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

    """
    Distribution (roughtly):

    NotificationStore:
        send = '/send'
        history
    
    
    FileStore:
        publish_file
        load_file

    
    UserStore:
        login
        logout
        register

    RoomStore:
        create_room
        delete_room
        add_user
        remove_user
        join_room
        leave_room
        start_private (create_room private = true)
        user_list

    help

    """
    