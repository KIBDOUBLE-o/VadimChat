import time

from addition import save_base64_to_file
from chat.chat_message_source import ChatMessageSource
from chunked.chunked_data import ChunkedData
from chunked.chunked_type import ChunkedType
from notificator import Notificator
from chat.coding.triplex64 import decode_triplex64


class ChunkedReceiverHelper:
    def __init__(self, callback):
        self.history = []
        self.assembling = {}
        self.callback = callback

    def add(self, item):
        self.history.append(item)

    def update_received_messages(self):
        if not self.history:
            time.sleep(0.05)
            return

        item = self.history.pop(0)
        try:
            sender, raw = item.split("/", 1)
            simple = ChunkedData.simple(raw)
            msg_type = simple.ch_type
            data_type = simple.type
            source = simple.source
            payload = simple.data
        except Exception as e:
            self.callback.debug_log(f"Parsing Error: {e}, raw={item}")
            return

        self.callback.debug_log(f"URM: TYPE: {msg_type}\nDATA_TYPE: {data_type}\nSOURCE: {source}\nSENDER: {sender}\nITEM: {item}\nPAYLOAD: {payload}")

        if sender not in self.assembling:
            self.assembling[sender] = []

        if msg_type == ChunkedType.Start:
            self.assembling[sender] = [payload]

        elif msg_type == ChunkedType.Nan:
            self.assembling[sender].append(payload)

        elif msg_type == ChunkedType.End:
            self.assembling[sender].append(payload)
            full_message = "".join(self.assembling[sender])
            if data_type == "[msg]":
                if full_message.startswith('safe*'):
                    self.callback.log(decode_triplex64(full_message), ChatMessageSource.Other, sender)
                else:
                    self.callback.log(full_message, ChatMessageSource.Other, sender)
                if self.callback.is_hidden:
                    Notificator.notify(f"{sender} пишет", payload)
                if self.callback.communicator.is_server: self.callback.make_history_impact(sender, full_message)
            elif data_type == "[file]":
                save_dir = f"data/shared_assets/"
                save_path = save_base64_to_file(full_message, save_dir, source)
                self.callback.log_file(save_path, ChatMessageSource.Other, sender)
                if self.callback.is_hidden:
                    Notificator.notify(f"{sender} прислал файл", save_path.split("/")[-1])
            elif data_type == '[button]':
                data = full_message.split(';')
                self.callback.ui.log_button(data[0], 'server', sender, data[1], data[2].split())

            self.callback.ui.plugin_manager.call_python_hook(self, 'crh.update_received_messages:end', locals(), globals())

            del self.assembling[sender]

        elif msg_type == ChunkedType.Both:
            full_message = payload
            if data_type == "[msg]":
                if full_message.startswith('safe*'):
                    self.callback.log(decode_triplex64(payload), ChatMessageSource.Other, sender)
                else:
                    self.callback.log(payload, ChatMessageSource.Other, sender)
                if self.callback.is_hidden:
                    Notificator.notify(f"{sender} пишет", payload)
            elif data_type == "[file]":
                save_dir = f"data/shared_assets/"
                save_path = save_base64_to_file(payload, save_dir, source)
                self.callback.log_file(save_path, ChatMessageSource.Other, sender)
                if self.callback.is_hidden:
                    Notificator.notify(f"{sender} прислал файл", save_path.split("/")[-1])
            elif data_type == '[button]':
                data = full_message.split(';')
                self.callback.ui.log_button(data[0], 'server', sender, data[1], data[2].split())

            self.callback.ui.plugin_manager.call_python_hook(self, 'crh.update_received_messages:end', locals(), globals())
