import socket
import ssl
from appdata import AppData


class Client:
    def __init__(self, connection: ssl.SSLSocket, addr: (str, int)):
        self.connection = connection
        self.addr = addr
        self.ip = addr[0]
        self.port = addr[1]

    def ask(self) -> str:
        return self.uask(self.connection)

    @staticmethod
    def uask(source) -> str:
        return source.recv(AppData.get_json("settings.json")["buffer_size"]).decode("utf-8")

    def send(self, data: str) -> None:
        self.connection.send(data.encode("utf-8"))
