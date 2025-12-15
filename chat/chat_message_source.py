from enum import Enum

class ChatMessageSource(Enum):
    Self = "me"
    Other = "other"
    Program = "server"
