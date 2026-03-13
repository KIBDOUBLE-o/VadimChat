import inspect
from typing import TYPE_CHECKING
from sys import setrecursionlimit
setrecursionlimit(9999999)

if TYPE_CHECKING:
    from chat.vadim_chat_ui import VadimChatUI


class StateManager:
    def __init__(self, callback: "VadimChatUI",
                 add_function=lambda name, t, value, path: None,
                 update_function=lambda data: None):
        self.callback = callback
        self.add = add_function
        self.update = update_function  # <-- оставляем как было

    def object_to_json(self, obj, _depth=0):
        if _depth > 10:
            return "<max depth>"

        if isinstance(obj, (bool, int, float, str)):
            return obj
        elif obj is None:
            return None
        elif callable(obj):
            args = []
            try:
                sig = inspect.signature(obj)
                for name, param in sig.parameters.items():
                    if name == "self":
                        continue
                    if param.default is not inspect.Parameter.empty:
                        args.append(f"{name}={param.default!r}")
                    elif param.kind == inspect.Parameter.VAR_POSITIONAL:
                        args.append(f"*{name}")
                    elif param.kind == inspect.Parameter.VAR_KEYWORD:
                        args.append(f"**{name}")
                    else:
                        args.append(name)
            except (ValueError, TypeError):
                args = ["..."]
            return {"__type__": "function", "args": args}
        elif isinstance(obj, (complex, bytes, bytearray)):
            try:
                return str(obj)
            except Exception:
                return "<unserializable>"
        elif isinstance(obj, (list, tuple)):
            return [self.object_to_json(v, _depth + 1) for v in obj]
        elif isinstance(obj, dict):
            result = {}
            for k, v in obj.items():
                key = str(k)
                if key.startswith("_"):
                    continue
                try:
                    result[key] = self.object_to_json(v, _depth + 1)
                except Exception:
                    result[key] = "<error>"
            return result
        else:
            result = {}
            for attr_name in dir(obj):
                if attr_name.startswith("_"):
                    continue
                try:
                    value = getattr(obj, attr_name)
                except Exception:
                    continue
                try:
                    result[attr_name] = self.object_to_json(value, _depth + 1)
                except Exception:
                    result[attr_name] = "<error>"
            return result

    def _get_roots(self):
        return {
            "chat": self.callback.chat,
            "plugin_manager": self.callback.plugin_manager,
        }

    def _resolve_path(self, parts: list):
        roots = self._get_roots()
        if not parts or parts[0] not in roots:
            return None
        obj = roots[parts[0]]
        for part in parts[1:]:
            try:
                if isinstance(obj, dict):
                    obj = obj[part]
                elif isinstance(obj, (list, tuple)):
                    obj = obj[int(part)]
                else:
                    obj = getattr(obj, part)
            except Exception:
                return None
        return obj

    def on_state_edit(self, path: str, value):
        self.apply_edit(path, value)

    def parse_internal_stats(self):
        try:
            new_tree = { "root": self.object_to_json(self.callback.chat) }
            self.update(new_tree)  # <-- оригинальный вызов
        except Exception as e:
            print(f"[StateManager] parse_internal_stats error: {e}")

    def apply_edit(self, path: str, value):
        parts = path.split("/")
        obj = self._resolve_path(parts[:-1])
        if obj is None:
            return
        key = parts[-1]
        try:
            if isinstance(obj, dict):
                existing = obj.get(key)
            else:
                existing = getattr(obj, key, None)
            if isinstance(existing, bool):
                value = value == "true" or value is True
            elif isinstance(existing, int):
                value = int(value)
            elif isinstance(existing, float):
                value = float(value)
            if isinstance(obj, dict):
                obj[key] = value
            else:
                setattr(obj, key, value)
        except Exception as e:
            print(f"[StateManager] apply_edit error: {e}")