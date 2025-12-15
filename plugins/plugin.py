import json

from plugins.python_hook import PythonHook


class Plugin:
    def __init__(self):
        self.id = 'NaN'
        self.display_name = 'Unnamed'
        self.description = ''
        self.author = ''
        self.version = '0.0.0'

        self.header = {}

        self.dependencies = []

        self.python = []
        self.webview = []

        self.enabled = True

    @staticmethod
    def load_plugin(name: str):
        plugin_path = f'data/plugins/{name}'
        plugin = Plugin()
        plugin.header = json.loads(open(f'{plugin_path}/header.json', encoding='utf-8').read())
        plugin.dependencies = plugin.header.get("dependencies", [])
        for py in plugin.header["py"]:
            plugin.python.append(PythonHook(py["hook"], open(f'{plugin_path}/{py["path"]}.py', encoding='utf-8').read()))
        for web in plugin.header["webview"]:
            plugin.webview.append((web["source"], open(f'{plugin_path}/{web["path"]}', encoding='utf-8').read(), {}))
        plugin.init_properties()
        return plugin

    def init_properties(self):
        self.id = self.header["id"]
        self.display_name = self.header["display_name"]
        self.author = self.header["author"]
        self.version = self.header["version"]
        self.description = self.header["description"]

    def __str__(self):
        return f"Plugin({self.id}) {{ dn: {self.display_name}, version: {self.version}, wv_size: {len(self.webview)} py_size: {len(self.python)} }}"
