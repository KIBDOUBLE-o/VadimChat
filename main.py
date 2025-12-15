import os

from appdata import AppData
from chat.vadim_chat_ui import VadimChatUI
from networking.network_communicator import NetworkCommunicator
#from networking.network_communicator_finder import find_servers
from plugins.plugin_manager import PluginManager

if __name__ == "__main__":
    print("Hello world")

    #if int(input()) > 0: print(find_servers(12345))

    plugin_manager = PluginManager()
    plugin_manager.load_plugins()

    chat = VadimChatUI("1.2.3 Release", plugin_manager)
    chat.run()
