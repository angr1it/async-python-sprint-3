from dataclasses import dataclass


@dataclass
class Meta:
    key: str
    user_name: str
    loggedin: bool
