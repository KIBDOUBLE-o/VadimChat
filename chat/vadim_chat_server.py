from addition import *
from appdata import AppData
from chat.chat_message_source import ChatMessageSource
from chat.chunked_receiving_helper import ChunkedReceiverHelper
from chunked.chunked_data import ChunkedData
from logger.log_type import LogType
from logger.logger import Logger
from networking.client import Client
from notificator import Notificator
import traceback


class VadimChatServer:
    def __init__(self, callback):
        self.callback = callback
        self.crh = ChunkedReceiverHelper(self.callback)
        self.any = {}

    def client_processing_start(self, client: Client, silence):
        try:
            if not silence: self.callback.ui.plugin_manager.call_python_hook(self, 'server.client_processing_start', locals(), globals())
            if not silence: self.callback.log(f"Пользователь '{get_key(self.callback.communicator.shortcuts, client.addr)}' подключён", ChatMessageSource.Program, "Server")
            #client.send(f"[history]{json.dumps(AppData.get_json("history.json"))}")
            if not silence: Logger.log("[SERVER] New client accepted!", LogType.INFO)
        except:
            if not silence: Logger.log('[SERVER] ' + traceback.format_exc(), LogType.ERROR)

    def client_processing(self, client: Client, received: str):
        self.callback.ui.plugin_manager.call_python_hook(self, 'server.client_processing:pre', locals(), globals())
        try:
            receiver_name = received.split(":")[0]
            msg = received[(len(receiver_name) + 1):]
            simple = ChunkedData.simple(msg)
            msg_part = simple.data
            self.callback.ui.plugin_manager.call_python_hook(self, 'server.client_processing:after_msg_work', locals(), globals())
            if msg_part.startswith("!"):
                self.proceed_command(f'{receiver_name}:{msg_part[1:]}', self.callback.is_operator_by_addr(client.addr))
                self.callback.ui.plugin_manager.call_python_hook(self, 'server.client_processing:command_proceed', locals(), globals())
                return

            self.callback.debug_log(f"MESSAGE BY [{client.addr}] : {msg} : FULL : {received}")
            self.crh.add(f"{receiver_name}/{msg}")
            self.crh.update_received_messages()
            if msg_part.startswith("--"): return
            self.callback.make_history_impact(receiver_name, f"{simple.type}{msg}")
        except:
            Logger.log('[SERVER] ' + traceback.format_exc(), LogType.ERROR)

    def on_client_disconnect(self, client: Client):
        self.callback.ui.plugin_manager.call_python_hook(self, 'server.on_client_disconnect:pre', locals(), globals())
        self.callback.log(f"Пользователь '{self.callback.get_user_name(client.addr)}' отключился!", ChatMessageSource.Program, "Server")

    def proceed_command(self, command, op=True):
        sender = command.split(':')[0]
        command = command.removeprefix(f'{sender}:')
        if command == "": return
        try:
            settings = AppData.get_json("settings.json")
            chunk_size = int(settings["data_chunk_size"])

            def fast_chunked(data: str) -> str:
                return ChunkedData(data, "[msg]", "", chunk_size).get_proceed()[0]

            data = command.split()
            root = data[0]
            first = data[1] if len(data) > 1 else ""
            second = data[2] if len(data) > 2 else ""
            other = command[(len(root) + len(first) + 2):]
            sother = other[(len(second) + 1):]

            if op:
                if root == "ban":
                    self.callback.communicator.ban(self.callback.get_user(first).addr)
                    self.callback.log(f"Пользователь '{first}' заблокирован!", ChatMessageSource.Program, "Server")
                elif root == "unban":
                    self.callback.communicator.unban(self.callback.get_user(first).addr)
                    self.callback.log(f"Пользоваель '{first}' разблокирован!", ChatMessageSource.Program, "Server")
                elif root == "kick":
                    client = self.callback.get_user(first)
                    self.callback.communicator.kick(client.addr)
                    self.callback.log(f"Пользователь '{first}' выкинут!", ChatMessageSource.Program, "Server")

                elif root == "admin":
                    self.callback.operators.append(self.callback.get_user(first).addr)
                    self.callback.log(f"Пользователь '{first}' теперь оператор!", ChatMessageSource.Program, "Server")
                    self.callback.get_user(first).send(f"Server:{fast_chunked("Вы теперь оператор!")}")
                elif root == "noadmin":
                    self.callback.operators.remove(self.callback.get_user(first).addr)
                    self.callback.log(f"Пользователь '{first}' больше не оператор!", ChatMessageSource.Program, "Server")
                    self.callback.get_user(first).send(f"Server:{fast_chunked("Вы больше не оператор!")}")

                elif root == "send":
                    self.callback.get_user(first).send(f"Server:{fast_chunked(f"*{other}")}\0")
                    self.callback.log(f"Отправлено на выполнение пользователю '{first}'!", ChatMessageSource.Program, "Server")
                    Logger.log(f'[SERVER] Код "{other}" отправлен на выполнение пользователю {first}', LogType.INFO)

                elif root == "ssend":
                    self.callback.get_user(first).send(f"Server:{fast_chunked(f's*{other}')}\0")
                    Logger.log(f'[SERVER] Код "{other}" бесшумно отправлен на выполнение пользователю {first}', LogType.INFO)

                elif root == "say":
                    if first == "all":
                        self.callback.communicator.send_all(f"Server:{fast_chunked(other)}")
                    else:
                        self.callback.get_user(first).send(f"Server:{fast_chunked(other)}")
                    self.callback.log(other, ChatMessageSource.Program, "Server")
                elif root == "sayby":
                    if first == "all":
                        self.callback.communicator.send_all(f"{second}:{fast_chunked(sother)}")
                    else:
                        self.callback.get_user(first).send(f"{second}:{fast_chunked(sother)}")
                    self.callback.log(sother, ChatMessageSource.Program, "Server")

                elif root == "flush":
                    if first == "history":
                        self.callback.flush_history()
                        self.callback.log(f"История сообщений очищена!", ChatMessageSource.Program, "Server")

                elif root == "!py":
                    try:
                        result = str(eval(command[4:]))
                    except Exception as e:
                        result = f"Инвалид? Ошибка: {e}"
                    self.callback.log(result, ChatMessageSource.Program, "Server")
                    Logger.log(f'[SERVER] Код "{command[4:]}" выполнен на сервере с результатом {result}', LogType.INFO)

                elif root == '$p':
                    pass


            if root == 'btn':
                self.callback.send_uni_all(f'{first};{second};{sother}', sender, 'button')
                self.callback.ui.log_button(first, 'server', sender, second, sother.split())
            elif root == 'table':
                self.callback.ui.log_table('table1', 'me', 'niga', ['name', 'points', 'level'], [
                    ['loh', '10', '1'],
                    ['nig', '11', '1']
                ])
            elif root == 'help':
                commands = [
                    ('ban', 'блокирует пользователя на время текущей сессии', ['shortcut']),
                    ('unban', 'разблокировивает пользователя в текущей сессии', ['shortcut']),
                    ('kick', 'отключает пользователя от сессии', ['shortcut']),
                    ('admin', 'даёт администраторские права пользователю', ['shortcut']),
                    ('noadmin', 'забирает администраторские права у пользователя', ['shortcut']),
                    ('send', 'отправляет код на выполнение другому пользователю', ['shortcut', 'type', 'code']),
                    ('ssend', 'тихо отправляет код на выполнение другому пользователю',
                     ['shortcut', 'type', 'code']),
                    ('say', 'отправляет сообщение от сервера', ['shortcut/"all"', 'message']),
                    ('sayby', 'отправляет сообщение от другого пользователя',
                     ['target shortcut/"all"', 'sender shortcut', 'message']),
                    ('flush', 'очищает указанный тип данных', ['type']),
                    ('!py', 'выполняет код на сервере', ['code']),
                    ('$p', 'делает интересные вещи', []),
                    ('btn', 'создаёт кнопку', ['title', 'id', 'button_title(1-5)']),
                    ('help', 'отображает список всех доступных команд', [])
                ]

                # Формируем строки таблицы
                rows = []
                for name, desc, args in commands:
                    arg_str = ' '.join(f'<{arg}>' for arg in args)  # собираем аргументы в строку
                    rows.append([name, arg_str, desc])

                # Заголовки таблицы
                columns = ['Команда', 'Аргументы', 'Описание']

                if sender == 'help':
                    self.callback.ui.log_table(
                        id='commands_table',
                        sender='Server',
                        name='Список команд',
                        columns=columns,
                        rows=rows
                    )
                else:
                    self.proceed_command(f'Server:ssend {sender} py self.callback.ui.log_table(id="commands_table", sender="Server", name="Список команд", columns={columns}, rows={rows})', True)

            self.callback.ui.plugin_manager.call_python_hook(self, 'server.command_proceed', locals(), globals())
            
            Logger.log(f"[SERVER] Received user command: '{command}' Details: (root: '{root}', first: '{first}', second: '{second}', other: '{other}')", LogType.INFO)

        except Exception as e:
            traceback.print_exc()
            self.callback.debug_log(traceback.format_exc())
            self.callback.log(f"Инвалид? Ошибка: {e}", ChatMessageSource.Program, "Server")
            Logger.log('[SERVER] ' + traceback.format_exc(), LogType.ERROR)