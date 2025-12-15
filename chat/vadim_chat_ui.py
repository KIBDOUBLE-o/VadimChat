import json
import os
import subprocess
import sys
import threading
import traceback

from PIL import Image
import pystray

import webview
from appdata import AppData
from chat.vadim_chat import VadimChat
from logger.log_type import LogType
from logger.logger import Logger
from networking.communicator_mode import CommunicatorMode
from addition import pack_file
from networking.network_communicator_finder import NetworkCommunicatorFinder
from plugins.plugin import Plugin
from plugins.plugin_applier import PluginApplier
from plugins.plugin_manager import PluginManager
from web.web_constructor import WebConstructor


class VadimChatUI:
    def __init__(self, version: str, plugin_manager: PluginManager):
        self.chat = VadimChat()
        self.hidden = False
        self.window = None
        self.LOG_ACCESS_LAMBDA = lambda msg, sender, name: self.log(msg, sender, name)
        self.version = version
        self.plugin_manager = plugin_manager
        self.pinger = None

    def log(self, msg: str, sender="other", name="Unknown"):
        self.plugin_manager.call_python_hook(self, 'ui.log:pre', locals(), globals())
        if self.window:
            self.window.evaluate_js(f'addMessage({repr(msg)}, "{sender}", {repr(name)});')

    def log_button(self, msg: str, sender="other", name="Unknown", id="NaN", buttons=None):
        if buttons is None:
            buttons = ['name']
        if len(buttons) > 5: return
        if self.window:
            self.call('addButtonMessage', msg, sender, name, id, buttons)

    def log_file(self, file_path, sender="other", name="Unknown"):
        self.plugin_manager.call_python_hook(self, 'ui.log_file:pre', locals(), globals())
        try:
            if self.window:
                self.call("addFileMessage", pack_file(file_path), sender, file_path.split("/")[-1], name)
                self.plugin_manager.call_python_hook(self, 'ui.log_file:before', locals(), globals())
        except Exception as e:
            print(e)

    def log_table(self, id, sender="other", name="Unknown", columns=None, rows=None):
        if rows is None:
            rows = []
        if columns is None:
            columns = []
        if self.window:
            self.call('sendTable', sender, id, columns, rows, name)

    def set_server_list(self, info):
        print(info)
        self.call('setServers', info)

    def minimize_to_tray(self, window):
        def show_window(icon):
            self.plugin_manager.call_python_hook(self, 'ui.minimize_to_tray:show_window', locals(), globals())
            icon.stop()
            window.show()
            self.hidden = False

        def quit_app(icon):
            self.plugin_manager.call_python_hook(self, 'ui.minimize_to_tray:quit_app', locals(), globals())
            icon.stop()
            window.destroy()

        def run_tray():
            self.plugin_manager.call_python_hook(self, 'ui.minimize_to_tray:run_tray', locals(), globals())
            try:
                self.hidden = True
                image = Image.open("data/chat/icon.ico")
                menu = pystray.Menu(
                    pystray.MenuItem("Открыть", lambda icon, item: show_window(icon)),
                    pystray.MenuItem("Выход", lambda icon, item: quit_app(icon))
                )
                icon = pystray.Icon("MyApp", image, "Vadim Chat", menu)
                icon.run()
            except:
                Logger.log(traceback.format_exc(), LogType.ERROR)

        self.plugin_manager.call_python_hook(self, 'ui.minimize_to_tray:pre', locals(), globals())
        window.hide()
        threading.Thread(target=run_tray, daemon=True).start()

    def send_file_from_ui(self, fileData):
        """
        fileData: dict { name: str, type: str, size: int, data: base64-string }
        вызывается из UI (pywebview API)."""

        self.plugin_manager.call_python_hook(self, 'ui.send_file_from_ui', locals(), globals())
        self.chat.send_file_self(fileData["data"], AppData.get_jvalue("settings", "nickname"), fileData["name"])

        #self.log(f"Файл '{name}' отправлен ({total} кусков).", "server", "Server")

    def close_chat(self):
        self.plugin_manager.call_python_hook(self, 'ui.close_chat', locals(), globals())
        self.chat = VadimChat()
        self.call("closeChat")

    def set_setting(self, id: str, value):
        self.plugin_manager.call_python_hook(self, 'ui.set_setting', locals(), globals())
        try:
            self.call(f'setSetting', id, value)
        except Exception as e:
            print(e)

    def add_plugin(self, plugin: Plugin):
        self.plugin_manager.call_python_hook(self, 'ui.add_plugin', locals(), globals())
        self.window.evaluate_js(f"""
            addPlugin({{
                id: {json.dumps(plugin.id)},
                display_name: {json.dumps(plugin.display_name)},
                description: {json.dumps(plugin.description)},
                version: {json.dumps(plugin.version)},
                author: {json.dumps(plugin.author)},
                enabled: {json.dumps(plugin.enabled)},
                onEnable: function() {{
                    logDebug("Плагин {plugin.display_name} активирован", "info");
                }},
                onDisable: function() {{
                    logDebug("Плагин {plugin.display_name} отключен", "info");
                }}
            }});
        """)

    def set_debug_state(self, state: bool):
        if state:
            self.call("enableDebug")
        else:
            self.call("disableDebug")

    def debug_log(self, message):
        self.call("logDebug", message)
        print(f"DEBUG: [{message}]")

    def call(self, func: str, *args):
        js_args = ", ".join(json.dumps(arg) for arg in args)
        self.window.evaluate_js(f"{func}({js_args});")

    def on_loaded(self):
        settings = AppData.get_json("settings.json")
        self.call("setVersion", self.version)
        self.call("setNickName", settings["nickname"])
        try:
            self.set_setting("default_ip", settings["default_ip"])
            self.set_setting("universal", settings["universal"])
            self.set_setting("use_universal", settings["use_universal"])
            self.set_setting("port", settings["port"])
            self.set_setting("buffer_size", settings["buffer_size"])
            self.set_setting("data_chunk_size", settings["data_chunk_size"])
            self.set_setting("chunk_sending_rate", settings["chunk_sending_rate"])
            self.set_setting("debug_mode", settings["debug_mode"])
        except Exception as e:
            print(f"Settings on_load applying error: {e}")
            Logger.log(f'[UI] Ошибка применения настроек при загрузке: {e}', LogType.INFO)
        self.pinger = NetworkCommunicatorFinder(int(settings["port"]))
        self.set_debug_state(settings["debug_mode"])

        self.plugin_manager.call_python_hook(self, 'ui.on_loaded', locals(), globals())

        for plugin in self.plugin_manager.plugins:
            self.add_plugin(plugin)
        #self.pinger.start_scan_loop()
        #self.pinger.start_visualize_loop(self)

    def run(self):
        class Api:
            def send_message(api_self, message):
                nick = AppData.get_json("settings.json")["nickname"]
                self.plugin_manager.call_python_hook(self, 'ui.api.send_message', locals(), globals())
                self.plugin_manager.call_python_hook(self, 'ui.api.send_any', locals(), globals())
                # self.log_button(message, "me", nick, "bob", '1', '2', '3')
                is_server = self.chat.communicator.is_server
                if message.startswith("!"):
                    if is_server:
                        self.chat.server.proceed_command(message[1:])
                    else:
                        self.chat.send_self(message, nick)
                else:
                    if is_server: self.chat.send_self_all(message, 'Server')
                    else: self.chat.send_self(message, nick)
                    self.log(message, "me", nick if not is_server else 'Server')
                    Logger.log(f'[UI] [{'CLIENT' if not self.chat.communicator.is_server else 'SERVER'}] Сообщение отправлено: {message}', LogType.INFO)

            def send_file(api_self, data):
                self.plugin_manager.call_python_hook(self, 'ui.api.send_file', locals(), globals())
                self.plugin_manager.call_python_hook(self, 'ui.api.send_any', locals(), globals())
                self.send_file_from_ui(data)

            def create_chat(api_self):
                self.plugin_manager.call_python_hook(self, 'ui.api.create_chat', locals(), globals())
                self.chat = VadimChat(CommunicatorMode.Server, ui=self)
                self.chat.run()
                print("SERVER LOG:")

            def join_chat(api_self, key, name):
                self.plugin_manager.call_python_hook(self, 'ui.api.join_chat', locals(), globals())
                self.chat = VadimChat(CommunicatorMode.Client, key=key, ui=self)
                self.chat.run()
                settings = AppData.get_json("settings.json")
                settings["nickname"] = name
                settings["key"] = key
                AppData.set_json("settings.json", settings)
                self.chat.communicator.send(name)
                print(f"[{name}] JOINS BY <{key}>")

            def exit_chat(api_self):
                self.plugin_manager.call_python_hook(self, 'ui.api.exit_chat', locals(), globals())
                self.chat.communicator.exit()
                self.chat = None

            def open_shared_folder(api_self, path: str):
                self.plugin_manager.call_python_hook(self, 'ui.api.open_shared_folder', locals(), globals())
                abs_path = os.path.abspath(path)
                if not os.path.exists(abs_path):
                    return f"Папка {abs_path} не найдена"
                if sys.platform.startswith("win"):
                    os.startfile(abs_path)
                elif sys.platform.startswith("darwin"):
                    subprocess.Popen(["open", abs_path])
                else:
                    subprocess.Popen(["xdg-open", abs_path])
                return f"Открыта папка: {abs_path}"

            def apply_settings(api_self, settings: dict):
                current_settings = AppData.get_json("settings.json")
                self.plugin_manager.call_python_hook(self, 'ui.api.apply_settings', locals(), globals())
                new_settings = {
                    "nickname": current_settings["nickname"],
                    "key": current_settings["key"]
                }
                for key in settings.keys():
                    if "adv" in key: continue
                    new_settings[key] = settings[key]
                AppData.set_json("settings.json", new_settings)
                self.set_debug_state(new_settings["debug_mode"])
                self.pinger.port = int(new_settings["port"])

            def reconnect(api_self):
                settings = AppData.get_json("settings.json")
                self.plugin_manager.call_python_hook(self, 'ui.api.reconnect', locals(), globals())
                api_self.join_chat(settings["key"], settings["nickname"])

            def minimize(api_self):
                self.minimize_to_tray(self.window)

            def hook(api_self, hook_key: str, data: dict):
                self.plugin_manager.call_python_hook(self, 'ui.api.new', locals(), globals())

            def button_pressed(api_self, id: str, index: int):
                self.plugin_manager.call_python_hook(self, 'ui.api.button_pressed', locals(), globals())

            def set_plugin_state(api_self, id: str, state: bool):
                for plugin in self.plugin_manager.plugins:
                    if plugin.id == id:
                        plugin.enabled = state
                        plugins_data = AppData.get_json('plugins.json')
                        for i in range(len(plugins_data)):
                            if plugins_data[i]['id'] == id:
                                plugins_data[i]['enabled'] = state
                        AppData.set_json('plugins.json', plugins_data)
                        exit()

            def refresh_servers(api_self):
                self.set_server_list([{'key': s['key'], 'name': s['source']} for s in self.pinger.find_servers()])

        constructor = WebConstructor()
        constructor.include_index(AppData.get("chat/chat_index.html"))
        constructor.include_style(AppData.get("chat/chat_style.css"))
        constructor.include_script(AppData.get("chat/chat_script.js"))

        index = PluginApplier.modify_index(self.plugin_manager.plugins, constructor.build())
        self.plugin_manager.call_python_hook(self, 'ui.init', locals(), globals())

        self.window = webview.create_window("Vadim Chat", html=index, js_api=Api(), text_select=True)
        webview.start(func=self.on_loaded)
