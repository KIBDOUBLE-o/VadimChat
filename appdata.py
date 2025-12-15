import json


class AppData:
    ENCODING = "utf-8"

    @staticmethod
    def get(path: str) -> str:
        return open(f"data/{path}", encoding=AppData.ENCODING).read()

    @staticmethod
    def get_json(path: str):
        return json.load(open(f"data/{path}", encoding=AppData.ENCODING))

    @staticmethod
    def get_jvalue(source: str, key: str, t=str):
        data = AppData.get_json(f"{source}.json")
        value = data.get(key)
        return t(value)

    @staticmethod
    def set(path: str, data: str) -> None:
        open(f"data/{path}", "w", encoding=AppData.ENCODING).write(data)

    @staticmethod
    def set_json(path: str, data) -> None:
        json.dump(data, open(f"data/{path}", "w", encoding=AppData.ENCODING), indent=4)

    @staticmethod
    def add(path: str, data: str) -> None:
        open(f"data/{path}", "a", encoding=AppData.ENCODING).write(data)
