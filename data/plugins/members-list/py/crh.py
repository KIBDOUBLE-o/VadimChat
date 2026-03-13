if data_type == '[mml]':
    if not self.callback.communicator.is_server:
        # self.callback.ui.call('setMembersList', [(shortcut, shortcut in self.callback.operators) for shortcut in list(self.callback.communicator.shortcuts.keys())])
        link("members-list:py/utils", "update_members_list", [self, full_message])