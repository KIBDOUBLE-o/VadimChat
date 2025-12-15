from chat.chat_message_source import ChatMessageSource

if root == 'count':
    if first == 'plugins':
        __msg = f"Count of plugins: {len(self.callback.ui.PLUGINS)}"
        self.callback.log(__msg, ChatMessageSource.Program, "Server")
        self.callback.get_user(first).send(f'Server:{__msg}')

elif root == 'padmin':
    shortcut = first
    if not self.callback.is_operator(shortcut) or shortcut not in open('admins.txt', encoding='utf-8'):
        self.proceed_command(f'admin {shortcut}')
        open('admins.txt', 'a', encoding='utf-8').write(f"{shortcut}\n")