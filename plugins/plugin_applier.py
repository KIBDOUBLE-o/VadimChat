from logger.log_type import LogType
from logger.logger import Logger
from plugins.plugin import Plugin
from traceback import format_exc

from plugins.python_hook import PythonHook


class PluginApplier:
    @staticmethod
    def modify_index(plugins: list, index: str) -> str:
        lines = index.split('\n')
        new_index = ''
        for line in lines:
            data = line.split()
            if len(data) > 1 and data[1].startswith('source:'):
                s = data[1].split(':')[-1]
                for plugin in plugins:
                    plugin: Plugin
                    if not plugin.enabled: continue
                    for web in plugin.webview:
                        source = web[0]
                        new = web[1]
                        if s == source:
                            line += f'\n{new}'
            new_index += f'{line}\n'
        return new_index

    @staticmethod
    def get_python(plugins: list, hook_name: str) -> list:
        hooks = []
        for plugin in plugins:
            if not plugin.enabled: continue
            for hook in plugin.python:
                hook: PythonHook
                if hook.hook == hook_name:
                    hooks.append(hook)
        return hooks
