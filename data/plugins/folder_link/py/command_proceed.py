if root == 'pubfolder':
    if 'public_folders' not in self.any: self.any['public_folders'] = []
    if first not in self.any['public_folders']:
        self.any['public_folders'].append(first)
        self.proceed_command(f':ssendall py if not os.path.exists("{first}"): os.mkdir("{first}")')
        self.proceed_command(f":ssendall py self.folders['{first}'] = []")
        self.proceed_command(f":ssend {sender} py self.callback.ui.log('Общая папка {first} создана!', 'server', 'Server')")
    else:
        self.proceed_command(f":ssend {sender} py self.callback.ui.log('Общая папка {first} уже существует!', 'server', 'Server')")

elif root == 'closefolder':
    if 'public_folders' not in self.any: self.any['public_folders'] = []
    else:
        if first in self.any['public_folders']:
            self.any['public_folders'].remove(first)
            self.proceed_command(f":ssendall py del self.folders['{first}']")
            self.proceed_command(f":ssend {sender} py self.callback.ui.log('Общая папка {first} закрыта!', 'server', 'Server')")
        else:
            self.proceed_command(f":ssend {sender} py self.callback.ui.log('Общей папки с именем {first} не существует!', 'server', 'Server')")
        
elif root == 'ssendall':
    self.callback.send_uni_all(f's*{command[(len(root) + 1):]}\0', 'Server', 'msg')