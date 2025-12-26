from chat.vadim_chat_ui import VadimChatUI
from plugins.plugin_manager import PluginManager

if __name__ == "__main__":
    print("Hello world")

    plugin_manager = PluginManager()
    plugin_manager.load_plugins()

    chat = VadimChatUI("1.2.7 Release", plugin_manager)
    chat.run()
