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
        self.chat_version = '0.0.0'

        self.header = {}

        self.python = []
        self.webview = []

        self.enabled = True

    @staticmethod
    def get_path(name: str):
        return f'data/plugins/{name}'

    @staticmethod
    def get_plugin_script(plugins: list, url: str) -> PythonHook or None:
        for plugin in plugins:
            for hook in plugin.python:
                hook: PythonHook
                if hook.url == url:
                    return hook
        print(f"Unknown script {url}")
        return None

    def continue_loading(self, dependency_check):
        plugin_path = Plugin.get_path(self.path_name)
        try:
            if self.header == {}:
                self.load_header(self.path_name, self.chat_version)

            if "dependencies" in self.header:
                for dependency in self.header["dependencies"]:
                    if not dependency_check(dependency):
                        return f'A required dependency "{dependency}" is missing'

            print("Python scripts loading")
            for py in self.header["py"]:
                paths = []
                if type(py["path"]) is list:
                    paths = py["path"]
                else:
                    paths.append(py["path"])
                for path in paths:
                    url = f'{self.id}:{path.replace('\\', '/')}'
                    hook = PythonHook(py["hook"], open(f'{plugin_path}/{path}.py', encoding='utf-8').read(), url)
                    self.python.append(hook)
                    print(f"Loading {path}{" "*(abs(40-len(path)))} as {url}")
            print("Webview loading")
            for web in self.header["webview"]:
                paths = []
                if web["path"] is list:
                    paths = web["path"]
                else:
                    paths.append(web["path"])
                for path in paths:
                    print(f"Loading {path}")
                    self.webview.append((web["source"], open(f'{plugin_path}/{path}', encoding='utf-8').read()))
            return ''
        except:
            return traceback.format_exc()

    def load_header(self, name: str, version: str):
        self.path_name = name
        plugin_path = Plugin.get_path(name)
        try:
            self.header = json.loads(open(f'{plugin_path}/header.json', encoding='utf-8').read())
            self.init_properties()
            if self.chat_version != version: return f'Old plugin chat version! Now {version}, but given {self.chat_version}'
            return ''
        except:
            return f'Header loading error:\n{traceback.format_exc()}'

    def init_properties(self):
        self.id = self.header["id"]
        self.display_name = self.header["display_name"]
        self.author = self.header["author"]
        self.version = self.header["version"]
        self.description = self.header["description"]
        self.chat_version = self.header["chat_version"]

    def __str__(self):
        return f"Plugin({self.id}) {{ dn: {self.display_name}, version: {self.version}, wv_size: {len(self.webview)} py_size: {len(self.python)} }}"
