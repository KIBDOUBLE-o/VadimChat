from datetime import datetime

from appdata import AppData
from logger.log_type import LogType


class Logger:
    @staticmethod
    def log(message: str, t: LogType):
        AppData.add("log.txt", f"[{t.value}] ({datetime.now().time()}) - {message}\n")
