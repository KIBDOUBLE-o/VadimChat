import json
import socket
import threading
import time
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed

from addition import get_key
from appdata import AppData
from networking.communicator_mode import CommunicatorMode
from networking.client import Client

class NetworkCommunicator:
    SPECIAL_PREFIX = "[[NET] - COMMUNICATIONREQUSET]"

    def __init__(self, mode: CommunicatorMode, port: int, ip="localhost",
                 on_new_connection=lambda client: None,
                 on_new_client_starts_processing=lambda client, silence: None,
                 on_client_disconnect=lambda client: None,
                 on_client_processing=lambda client, received: None,
                 on_client_connected=lambda sock, addr: None,
                 on_client_receiving_processing=lambda sock, addr, received: None,
                 on_client_disconnected=lambda sock: None,
                 on_client_starts_receiving_processing=lambda sock, addr: None,
                 on_started=lambda: None,
                 pinger=False):
        self.mode = mode
        self.port = port
        self.ip = ip
        self.clients = { }
        self.shortcuts = { }
        self.banned = []
        self.pinger = pinger

        self.current = None
        self.server_socket = None

        # Events
        self.on_started = on_started
        # Server
        self.on_new_connection = on_new_connection
        self.on_new_client_starts_processing = on_new_client_starts_processing
        self.on_client_disconnect = on_client_disconnect
        self.on_client_processing = on_client_processing
        # Client
        self.on_client_connected = on_client_connected
        self.on_client_starts_receiving_processing = on_client_starts_receiving_processing
        self.on_client_receiving_processing = on_client_receiving_processing
        self.on_client_disconnected = on_client_disconnected
        # ------------

        self.stopped = False

    @property
    def self_ip(self) -> str:
        return socket.gethostbyname(socket.gethostname())

    @property
    def ip_data(self) -> list:
        return self.self_ip.split(".")

    @property
    def is_server(self) -> bool:
        return self.mode == CommunicatorMode.Server

    def register_client(self, connection, addr, shortcut) -> Client:
        self.clients[addr] = Client(connection, addr)
        self.shortcuts[shortcut] = addr
        print(f"Client {addr} with shortcut '{shortcut}' registered!")
        return self.clients[addr]

    def delete_client(self, addr: (str, int)) -> None:
        del self.clients[addr]

    def get_client(self, addr: (str, int)) -> Client or None:
        return self.clients.get(addr)

    def disconnect_client(self, client: Client) -> None:
        self.on_client_disconnect(client)
        client.connection.close()
        self.delete_client(client.addr)

    def get_shortcut(self, addr: (str, int)) -> str:
        return get_key(self.shortcuts, addr)

    def start(self):
        if self.is_server:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind(("0.0.0.0", self.port))
            self.server_socket.listen()
            threading.Thread(target=self.__server_loop__, args=(self.server_socket,), daemon=True).start()
        else:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            addr = (self.ip, self.port)
            sock.connect(addr)
            self.current = sock
            self.on_client_connected(sock, addr)
            threading.Thread(target=self.__client_receiving_processing__, args=(sock, addr), daemon=True).start()
        self.on_started()

    def send(self, data):
        if self.mode == CommunicatorMode.Client and hasattr(self, "current"):
            self.current.send(data.encode("utf-8"))

    def sendall(self, data):
        if self.mode == CommunicatorMode.Client and hasattr(self, "current"):
            self.current.sendall(data.encode("utf-8"))

    def send_all(self, data):
        """Send data to all connected clients (Server only)"""
        for client in self.clients.values():
            client.send(data)

    def __server_loop__(self, server):
        """Processing main server loop"""
        while True:
            if self.stopped: break
            conn, addr = server.accept()
            if addr in self.banned:
                conn.close()
                continue

            received = conn.recv(4096).decode("utf-8")
            client = self.register_client(conn, addr, received)

            self.on_new_connection(client)
            non_one = []
            to_kick = []
            contains = []
            for shortcut in self.shortcuts.keys():
                if shortcut in contains: non_one.append(shortcut)
                contains.append(shortcut)
            for shortcut in contains:
                if shortcut in non_one:
                    to_kick.append(shortcut)
            for shortcut in to_kick:
                self.kick(self.shortcuts[shortcut])
            threading.Thread(target=self.__client_processing__, args=(client,)).start()

    def __client_processing__(self, client):
        """Processing client on server side"""
        self.on_new_client_starts_processing(client, self.get_shortcut(client.addr).startswith('\0pinger\0'))
        while True:
            try:
                received = client.ask()
                if received.startswith(NetworkCommunicator.SPECIAL_PREFIX):
                    full_request = received[len(NetworkCommunicator.SPECIAL_PREFIX):]
                    type = full_request.split()[0]
                    request = full_request[(len(type) + 1):]
                    if type == "data":
                        client.send(json.dumps(self.self_data))
                    client.connection.close()
                    self.delete_client(client.addr)
                    return
                self.on_client_processing(client, received)
                for c in self.clients.values():
                    if c == client: continue
                    try: c.send(received)
                    except Exception:
                        self.disconnect_client(c)
                        return
            except ConnectionError:
                break
            except Exception as e:
                print(f"Client Processing Error: {e}")
                self.disconnect_client(client)
                return

        if client.addr in self.clients: self.disconnect_client(client)

    def __client_receiving_processing__(self, sock, addr):
        """Processing client receiving on client side"""
        self.on_client_starts_receiving_processing(sock, addr)
        while True:
            try:
                received = Client.uask(sock)
                self.on_client_receiving_processing(sock, addr, received)
            except Exception as e:
                print(f"Client Receiving Processing Error: {e}")
                traceback.print_exc()
                self.on_client_disconnected(None)
                break

        self.on_client_disconnected(sock)

    def exit(self):
        """Корректно завершает сервер или клиент."""
        self.stopped = True

        # Если это сервер — закрываем все клиенты и серверный сокет
        if self.is_server:
            for client in list(self.clients.values()):
                try:
                    client.connection.close()
                except:
                    pass
            self.clients.clear()

            try:
                self.server_socket.close()
            except Exception as e:
                print(f"[Server exit] Ошибка при закрытии сокета: {e}")
        else:
            if self.current:
                try:
                    self.current.close()
                except Exception as e:
                    print(f"[Client exit] Ошибка при закрытии: {e}")

    @property
    def self_data(self):
        _,_,x,y = self.self_ip.split('.')
        key = f'{x}{y}{len(x)}'
        nick = AppData.get_jvalue('settings', 'nickname')
        return {
            "connections_count": len(self.clients),
            "banned": self.banned,
            "ip": self.ip,
            "port": self.port,
            "key": key,
            "source": "Unknown" if nick == "" else nick
        }

    def ban(self, addr: (str, int)):
        self.banned.append(addr)
        self.kick(addr)

    def unban(self, addr: (str, int)):
        self.banned.remove(addr)

    def kick(self, addr: (str, int)):
        self.disconnect_client(self.get_client(addr))
