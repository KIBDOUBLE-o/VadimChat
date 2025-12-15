import socket
import json
import time
from threading import Thread
from concurrent.futures import ThreadPoolExecutor, as_completed


class NetworkCommunicatorFinder:
    TIMEOUT = 0.2
    THREADS = 80       # умеренное количество потоков

    def __init__(self, port):
        self.port = port
        self.actual = []

    def try_ping(self, ip, port):
        """Пробует корректно обратиться к серверу NetworkCommunicator."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.TIMEOUT)

            sock.connect((ip, port))

            # правило протокола — сначала shortcut
            sock.send(b"\0pinger\0scanner")

            time.sleep(0.03)  # чтобы сервер успел зарегистрировать клиента

            # теперь отправляем запрос
            sock.send(b"[[NET] - COMMUNICATIONREQUSET] data")

            data = sock.recv(4096).decode("utf-8")
            sock.close()

            try:
                return json.loads(data)
            except:
                return None

        except:
            return None


    def find_servers(self):
        """Сканирует только A.B.C.* — не нагружает систему."""
        local_ip = socket.gethostbyname(socket.gethostname())
        a, b, c, _ = local_ip.split(".")
        prefix = f"{a}.{b}.{c}"

        ips = [f"{prefix}.{i}" for i in range(1, 255)]
        results = []

        with ThreadPoolExecutor(max_workers=self.THREADS) as executor:
            futures = {executor.submit(self.try_ping, ip, self.port): ip for ip in ips}

            for future in as_completed(futures):
                data = future.result()
                if data:
                    results.append(data)

        return results

    def scan_loop(self):
        while True:
            self.actual = self.find_servers()
            time.sleep(0.333)

    def start_scan_loop(self):
        Thread(target=self.scan_loop, daemon=True).start()

    def visualize_loop(self, ui):
        while True:
            ui.set_server_list([f'{{ key: "{s['key']}", name: "{s['source']}" }}' for s in self.actual])
            time.sleep(1)

    def start_visualize_loop(self, ui):
        Thread(target=self.visualize_loop(ui), daemon=True).start()
