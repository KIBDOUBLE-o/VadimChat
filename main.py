from chat.vadim_chat_ui import VadimChatUI
from plugins.plugin_manager import PluginManager
from addition import *
from hashlib import sha256

if __name__ == "__main__":
    print("Hello world")

    version = "1.3"

    plugin_manager = PluginManager(version)
    plugin_manager.load_plugins()

    chat = VadimChatUI(version, "Release", plugin_manager)
    chat.run()
    #print(create_secret_key("вадимлох.exe"))
    #print("".join([hex(ord(c)) for c in "вадимлох.exe"]))
    #print(find_similar("Helo world!", ["Hello!", "Hello world!", "Hello world!!!"]))
