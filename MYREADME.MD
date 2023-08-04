
# Дополнительные требования (отметить [Х] выбранные пункты):

- [ ] (1 балл) Период жизни доставленных сообщений — 1 час (по умолчанию).
- [ ] (1 балл) Клиент может отправлять не более 20 (по умолчанию) сообщений в общий чат в течение определенного периода — 1 час (по умолчанию). В конце каждого периода лимит обнуляется.
- [ ] (1 балл) Возможность комментировать сообщения.
- [ ] (2 балла) Возможность создавать сообщения с заранее указанным временем отправки; созданные, но не отправленные сообщения можно отменить.
- [ ] (2 балла) Возможность пожаловаться на пользователя. При достижении лимита в 3 предупреждения, пользователь становится «забанен» — невозможность отправки сообщений в течение 4 часов (по умолчанию).
- [X] (3 балла) Возможность отправлять файлы различного формата (объёмом не более 5Мб, по умолчанию).
- [O] (3 балла) Возможность создавать кастомные приватные чаты и приглашать в него других пользователей. Неприглашенный пользователь может «войти» в такой чат только по сгенерированной ссылке и после подтверждения владельцем чата.  -- Нет ссылки, значит не выполнено?
- [X] (4 балла) Пользователь может подключиться с двух и более клиентов одновременно. Состояния должны синхронизироваться между клиентами.
- [ ] **(5 баллов) Реализовать кастомную реализацию для взаимодействия по протоколу `http` (можно использовать `asyncio.streams`);


# О решении
1. Запустить модуль chat.server;
2. Запустить модуль chat.client;
3. В консоли клиента вводить комадны:

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
