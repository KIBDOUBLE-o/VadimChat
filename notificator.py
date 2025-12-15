import os
import sys
from win10toast import ToastNotifier


class Notificator:
    @staticmethod
    def notify(title: str, message: str, timeout=5):
        try:
            icon_path = "data/chat/icon.ico"
            ToastNotifier().show_toast(
                title,
                message,
                icon_path=icon_path if os.path.exists(icon_path) else None,
                duration=timeout,
                threaded=True  # чтобы не блокировал интерфейс
            )
        except Exception as e:
            print(f"[Notify Error] {e}")
