import json
import socket
import time
from threading import Thread

from appdata import AppData
from chat.chat_message_source import ChatMessageSource
from chat.vadim_chat_client import VadimChatClient
from chat.vadim_chat_server import VadimChatServer
from chunked.chunked_data import ChunkedData
from networking.network_communicator import NetworkCommunicator
from networking.communicator_mode import CommunicatorMode
from addition import get_key
from plugins.plugin_applier import PluginApplier


class VadimChat:
    def __init__(self, mode=CommunicatorMode.Server, key="001", ui=None):
        settings = AppData.get_json("settings.json")
        self.client = VadimChatClient(self)
        self.server = VadimChatServer(self)
        self.ui = ui
        self.key = key
        self.communicator = NetworkCommunicator(
            mode=mode,
            port=int(settings["port"]),
            on_new_client_starts_processing=lambda client, silence: self.server.client_processing_start(client, silence),
            on_client_processing=lambda client, received: self.server.client_processing(client, received),
            on_client_receiving_processing=lambda sock, addr, received: self.client.client_receiving_processing(sock, addr, received),
            on_client_disconnected=lambda sock: self.client.on_client_disconnect(sock),
            on_client_disconnect=lambda client: self.server.on_client_disconnect(client),
            on_client_starts_receiving_processing=lambda sock, addr: self.client.client_receiving_start(sock, addr),
            on_started=lambda: self.on_started()
        )
        self.communicator.ip = f"{self.communicator.ip_data[0]}.{self.communicator.ip_data[1]}.{settings["universal"].replace("x", self.unpacked_key[0]).replace("y", self.unpacked_key[1])}" if settings["use_universal"] == True else settings["default_ip"].replace("x", self.unpacked_key[0]).replace("y", self.unpacked_key[1])
        #self.communicator.on_new_connection = lambda client: self.ui_message(f"Client connected: {client.addr}", "server", "Server")

        self.operators = []
        self.storage = {}

    @property
    def current_key(self) -> str:
        ip_data = self.communicator.self_ip.split(".")
        return f"{ip_data[-2]}{ip_data[-1]}{len(ip_data[-2])}"

    @property
    def unpacked_key(self) -> list:
        if not self.key or not self.key[-1].isdigit():
            return []

        length = int(self.key[-1])
        body = self.key[:-1]
        first = body[:length]
        second = body[length:]

        return [first, second]

    @property
    def is_hidden(self):
        return self.ui.hidden

    def log(self, message, source: ChatMessageSource, sender_name):
        self.ui.log(message, source.value, sender_name)

    def log_file(self, path, source: ChatMessageSource, sender_name):
        self.ui.log_file(path, source.value, sender_name)

    def debug_log(self, message):
        self.ui.debug_log(message)

    def get_user(self, name):
        return self.communicator.clients[self.communicator.shortcuts[name]]

    def get_user_name(self, addr: (str, int)):
        return get_key(self.communicator.shortcuts, addr)

    def save_data(self, path: str, data):
        current = self.storage
        keys = path.split('/')

        for key in keys[:-1]:
            is_index = key.isdigit()
            idx = int(key) if is_index else key

            if is_index:
                if not isinstance(current, list):
                    current = {}
                if idx >= len(current):
                    current.extend([{}] * (idx - len(current) + 1))
            else:
                if not isinstance(current, dict):
                    current = {}
                if idx not in current:
                    current[idx] = {}

            current = current[idx]

        if keys[-1]:
            last = keys[-1]
            is_index = last.isdigit()
            idx = int(last) if is_index else last

            if is_index:
                if not isinstance(current, list):
                    current = []
                if idx >= len(current):
                    current.extend([None] * (idx - len(current) + 1))

            current[idx] = data

    def get_data(self, path: str, default=None):
        """
        Получает данные из self.storage по иерархическому пути.

        Пример:
            path = "users/john/settings"
            Возвращает: self.storage["users"]["john"]["settings"]
        """
        current = self.storage
        keys = path.split('/')

        for key in keys:
            if not key:  # Пропускаем пустые ключи
                continue

            is_index = key.isdigit()
            idx = int(key) if is_index else key

            # Проверяем тип и наличие ключа
            if is_index:
                if not isinstance(current, list):
                    return default
                if idx >= len(current):
                    return default
            else:
                if not isinstance(current, dict):
                    return default
                if idx not in current:
                    return default

            current = current[idx]

        return current

    def ensure_path(self, path: str, default=None):
        """
        Проверяет существует ли путь, если нет - создает его.
        Возвращает конечный элемент пути (созданный или существующий).

        Пример:
            ensure_path("a/b/c") создаст: storage["a"]["b"]["c"] = None
            и вернет storage["a"]["b"]["c"]
        """
        if not hasattr(self, 'storage'):
            self.storage = {}

        current = self.storage
        keys = [k for k in path.split('/') if k]  # Убираем пустые элементы

        if not keys:  # Пустой путь
            return current

        # Проходим по всем ключам пути
        for i, key in enumerate(keys):
            is_last = (i == len(keys) - 1)

            # Решаем, что создавать в зависимости от типа ключа
            if key.isdigit():
                idx = int(key)
                # Если ожидается массив
                if not isinstance(current, list):
                    # Если текущий элемент - словарь, проверяем наличие ключа
                    if isinstance(current, dict) and idx in current:
                        value = current[idx]
                    else:
                        # Создаем список для числовых индексов
                        value = []
                    current = current if isinstance(current, dict) else {}
                    current[idx] = value

                if isinstance(current, list):
                    # Расширяем список если нужно
                    if idx >= len(current):
                        extend_by = idx - len(current) + 1
                        current.extend([default if is_last else {}] * extend_by)

                    if is_last:
                        return current[idx]
                    current = current[idx]
                else:
                    return None
            else:
                # Строковый ключ - словарь
                if not isinstance(current, dict):
                    return None

                if key not in current:
                    # Создаем новый узел
                    current[key] = default if is_last else {}

                if is_last:
                    return current[key]
                current = current[key]

        return current

    def send_uni(self, message: str, sender: str, t: str):
        self.ui.plugin_manager.call_python_hook(self, 'chat.send', locals(), globals())
        chunked = ChunkedData(message, f"[{t}]", "", AppData.get_jvalue("settings", "data_chunk_size", int)).get_proceed()
        for chunk in chunked:
            self.communicator.send(f"{sender}:{chunk}")
            time.sleep(AppData.get_jvalue("settings", "chunk_sending_rate", float))

    def send_uni_all(self, message: str, sender: str, t: str):
        self.ui.plugin_manager.call_python_hook(self, 'chat.send', locals(), globals())
        chunked = ChunkedData(message, f"[{t}]", "", AppData.get_jvalue("settings", "data_chunk_size", int)).get_proceed()
        for chunk in chunked:
            self.communicator.send_all(f"{sender}:{chunk}")
            time.sleep(AppData.get_jvalue("settings", "chunk_sending_rate", float))

    def send_self(self, message: str, sender: str):
        self.send_uni(message, sender, "msg")

    def send_self_all(self, message: str, sender: str):
        self.send_uni_all(message, sender, "msg")

    def send_file_self(self, data: str, sender: str, source: str):
        chunked = ChunkedData(data, "[file]", source, AppData.get_jvalue("settings", "data_chunk_size", int)).get_proceed()
        for chunk in chunked:
            self.communicator.send(f"{sender}:{chunk}")
            time.sleep(AppData.get_jvalue("settings", "chunk_sending_rate", float))

    def is_operator_by_addr(self, addr):
        return addr in self.operators

    def is_operator(self, name):
        return self.is_operator_by_addr(self.communicator.shortcuts[name])

    def on_started(self):
        self.log(f"Локальный код : {self.current_key}", ChatMessageSource.Program, "Server")
        # if self.communicator.is_server: self.restore_history()

    def make_history_impact(self, master: str, message: str):
        history = AppData.get_json("history.json")
        history.append({
            "master": master,
            "message": f'[msg]{message}'
        })
        AppData.set_json("history.json", history)

    def flush_history(self):
        AppData.set_json("history.json", [])

    def restore_history(self):
        try:
            history = AppData.get_json("history.json")
            settings = AppData.get_json("settings.json")
            for entry in history:
                _type = str(entry["message"]).split("]")[0][1:]
                other = str(entry["message"])[(len(_type) + 2):]
                master = str(entry["master"])
                sender = "me" if master == str(settings["nickname"]) else "other"
                if _type == "msg":
                    self.ui.log(ChunkedData.simple(other).data, sender, master)
        except: pass

    @staticmethod
    def plugins_update(self):
        while True:
            self.ui.plugin_manager.call_python_hook(self, 'server.plugin_update', locals(), globals(), log=False)
            time.sleep(0.3334)

    def run(self):
        self.communicator.start()
        if self.communicator.is_server:
            Thread(target=self.plugins_update, args=(self,), daemon=True).start()
