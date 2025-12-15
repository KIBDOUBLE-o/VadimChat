import os
from traceback import format_exc

from appdata import AppData
from logger.log_type import LogType
from logger.logger import Logger
from plugins.plugin import Plugin
from plugins.plugin_applier import PluginApplier
from plugins.python_hook import PythonHook


class PluginManager:
    def __init__(self):
        self.plugins = []
        self.errors = []

    def load_plugins(self):
        plugins = []
        for name in os.listdir("data/plugins"):
            plugin = Plugin()
            self.errors.append((name, plugin.load_header(name)))
            plugins.append(plugin)
        print(f'Header loading: {', '.join([str(plugin) for plugin in plugins])}')
        for plugin in plugins:
            try:
                self.errors.append((plugin.header["id"], plugin.continue_loading(lambda id: self.containment_check(id))))
            except: pass
        print(f'Plugins are loaded finally')

        plugins_data = AppData.get_json('plugins.json')
        for plugin in plugins:
            skip = False
            for data in plugins_data:
                if data['id'] == plugin.id:
                    plugin.enabled = data['enabled']
                    skip = True
            if skip: continue
            plugins_data.append({
                "id": plugin.id,
                "enabled": plugin.enabled
            })
        AppData.set_json('plugins.json', plugins_data)
        self.plugins = plugins

    def containment_check(self, id):
        return len([plugin for plugin in self.plugins if plugin.header["id"] == id]) > 0

    def call_python_hook(self, _self, hook_type, _locals, _globals, log=True):
        """Выполняет код с локальными переменными вызывающего метода"""
        # self.env = {**self.env, **_globals}
        for hook in PluginApplier.get_python(self.plugins, hook_type):
            hook: PythonHook
            try:
                _locals['self'] = _self
                hook.local = {**hook.local, **_locals, **_globals}
                # self.env = {**self.env, **hook.local}
                exec(hook.code, hook.local, hook.local)
                if log:
                    print(f"[OK] Plugin #{len(hook.code)} ({hook_type}) выполнен")
                    Logger.log(f"[OK] Plugin #{len(hook.code)} ({hook_type}) executed", LogType.INFO)
            except Exception as e:
                tb = format_exc()
                exception = ''
                exception += "\n" + "=" * 80
                exception += f"[ERROR] Ошибка во время выполнения plugin #{len(hook.code)} (hook: {hook_type})\n"
                exception += "-" * 80 + "\n"
                exception += "🧩 Код плагина:\n"
                exception += hook.code + "\n"
                exception += "-" * 80 + "\n"
                exception += f"❗ Тип ошибки: {type(e).__name__}\n"
                exception += f"❗ Сообщение: {e}\n"
                exception += "-" * 80 + "\n"
                exception += "📌 Traceback:\n"
                exception += tb + "\n"
                exception += "=" * 80 + "\n"
                print(exception)
                Logger.log(exception, LogType.ERROR)