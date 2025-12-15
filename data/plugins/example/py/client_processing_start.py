import os
exists = os.path.exists('admins.txt')
print(exists)
if exists:
    admins = open('admins.txt', encoding='utf-8').read().split('\n')
    client_shortcut = self.callback.get_user_name(client.addr)
    if client_shortcut in admins:
        self.proceed_command(f'admin {client_shortcut}')