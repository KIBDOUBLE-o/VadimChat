import os
from traceback import format_exc

from addition import find_similar
from appdata import AppData
from debugging.log_type import LogType
from debugging.logger import Logger
from plugins.plugin import Plugin
from plugins.plugin_applier import PluginApplier
from plugins.python_hook import PythonHook


class PluginManager:
    def __init__(self, version):
        self.version = version
        self.plugins = []
        self.errors = []
        self.env = {}
        self.current_hook = None
        self.make_it_global = False

    def load_plugins(self):
        plugins = []
        for name in os.listdir("data/plugins"):
            plugin = Plugin()
            self.errors.append((name, plugin.load_header(name, self.version)))
            plugins.append(plugin)
        print(f'Header loading: \n -{'\n -'.join([str(plugin) for plugin in plugins])}')
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

    def call_plugin_method(self, url: str, target: str, args: list):
        hook = Plugin.get_plugin_script(self.plugins, url)
        if hook:
            local = hook.local
            if target in local:
                if callable(local[target]):
                    return local[target](*args)
                else:
                    return local[target]
        print(f"Unknown url: {url} did you mean: {self.find_similar_url(url)}?")
        return None

    def find_similar_url(self, url) -> str:
        variants = []
        for plugin in self.plugins:
            for hook in plugin.python:
                variants.append(hook.url)
        return find_similar(url, variants)

    def load_hook_local(self, i_local: dict, url: str) -> dict:
        script = Plugin.get_plugin_script(self.plugins, url)
        if script is None: return i_local
        local = script.local
        return {**i_local, **local}

    def call_python_hook(self, _self, hook_type, _locals, _globals, log=True):
        """Выполняет код с локальными переменными вызывающего метода"""
        for hook in PluginApplier.get_python(self.plugins, hook_type):
            hook: PythonHook
            self.make_it_global = False
            try:
                self.current_hook = hook

                def load(url: str):
                    script = Plugin.get_plugin_script(self.plugins, url)
                    if not script:
                        return
                    self.current_hook.local.update(script.local)

                def make_global():
                    self.make_it_global = True

                _locals['self'] = _self
                _locals['link'] = lambda url, target, args: self.call_plugin_method(url, target, args)
                _locals['load'] = load
                _locals['make_global'] = make_global

                hook.local.update(_globals)
                hook.local.update(self.env)
                hook.local.update(_locals)

                exec(hook.code, hook.local, hook.local)

                if self.make_it_global:
                    denied_keys = ['link', 'load', 'make_global']
                    for key, value in hook.local.items():
                        if key not in denied_keys:
                            if not key.startswith('_'):
                                self.env[key] = value

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