from typing import List
import json

from ..command_types import CommandType

class ActionMessages:
    @staticmethod
    def left_room(username: str, room: str, shame):
        return {'action': 'left', 'room': room, 'user': username, 'shame': shame}
    
    @staticmethod
    def join_room(username: str, room: str, success: bool, message: str):
        return {'action': CommandType.join_room, 'success': success, 'user': username, 'room': room, 'message': message}
    
    @staticmethod
    def connecting(username: str, room: str):
        return {'action': 'connecting', 'room': room, 'user': username}
    
    @staticmethod
    def register(username: str, success: bool, reason: str):
        return {'action': CommandType.register, 'success': success, 'user': username, 'reason': reason}
    
    @staticmethod
    def login(username: str, success: bool, reason: str):
        return {'action': CommandType.login, 'success': success, 'user': username, 'reason': reason}
    
    @staticmethod
    def logout(username: str, success: bool, reason: str):
        return {'action': CommandType.login, 'success': success, 'user': username, 'reason': reason}
    
    @staticmethod
    def change_username(from_username: str, to_username: str, room: str):
        return {
            'action': CommandType.set_name,
            'success': True,
            'room': room,
            'from_user': from_username,
            'to_user': to_username,
        }
    
    @staticmethod
    def send_message_room(username: str, message: str):
        return {'action': CommandType.send, 'message': message, 'user': username}
    
    @staticmethod
    def send_message_accepted(message: str):
        return {'action': CommandType.send, 'success': True, 'message': message}
    
    @staticmethod
    def user_list(room: str, users: List[str]):
        return {'action': CommandType.user_list, 'success': True, 'room': room, 'users': users}
    
    @staticmethod
    def history(room: str, success: bool, n: int, content: List):
        return {
            'action': CommandType.history,
            'room': room,
            'n': n,
            'success': success,
            'content': json.dumps(content, default=str)
            }