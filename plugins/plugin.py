import json
import traceback

from plugins.python_hook import PythonHook


class Plugin:
    def __init__(self):
        self.path_name = ''

        self.id = 'NaN'
        self.display_name = 'Unnamed'
        self.description = ''
        self.author = ''
        self.version = '0.0.0'

        self.header = {}

        self.python = []
        self.webview = []

        self.enabled = True

    @staticmethod
    def get_path(name: str):
        return f'data/plugins/{name}'

    def continue_loading(self, dependency_check):
        plugin_path = Plugin.get_path(self.path_name)
        try:
            if self.header == {}:
                self.load_header(self.path_name)

            if "dependencies" in self.header:
                for dependency in self.header["dependencies"]:
                    if not dependency_check(dependency):
                        return f'A required dependency "{dependency}" is missing'

            for py in self.header["py"]:
                self.python.append(PythonHook(py["hook"], open(f'{plugin_path}/{py["path"]}.py', encoding='utf-8').read()))
            for web in self.header["webview"]:
                self.webview.append((web["source"], open(f'{plugin_path}/{web["path"]}', encoding='utf-8').read(), {}))
            self.init_properties()
            return ''
        except:
            return traceback.format_exc()

    def load_header(self, name: str):
        self.path_name = name
        plugin_path = Plugin.get_path(name)
        try:
            self.header = json.loads(open(f'{plugin_path}/header.json', encoding='utf-8').read())
            return ''
        except:
            return f'Header loading error:\n{traceback.format_exc()}'

    def init_properties(self):
        self.id = self.header["id"]
        self.display_name = self.header["display_name"]
        self.author = self.header["author"]
        self.version = self.header["version"]
        self.description = self.header["description"]

    def __str__(self):
        return f"Plugin({self.id}) {{ dn: {self.display_name}, version: {self.version}, wv_size: {len(self.webview)} py_size: {len(self.python)} }}"
