from dataclasses import dataclass

@dataclass
class Meta:
    username: str
    room: str
    loggedin: bool