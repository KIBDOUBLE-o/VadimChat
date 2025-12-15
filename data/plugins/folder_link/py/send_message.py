import os

def folders_av() -> bool:
    try:
        a = self.chat.client.folders
        return True
    except:
        return False
    
def proceed_folder(path) -> list:
    folder = []
    for file in os.listdir(path):
        if os.path.isdir(file):
            folder.append((file, proceed_folder(file)))
        else:
            folder.append((file, open(file, encoding='utf-8').read()))
    return folder

if message.startswith('!'):
    if not folders_av(): self.chat.client.folders = {}
    data = message[1:].split()
    if data[0] == 'pubfolder':
        folder = proceed_folder(data[1])
        self.chat.client.folders[data[1]] = folder
    elif data[0] == 'closefolder':
        del self.chat.client.folders[data[1]]