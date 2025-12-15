if hook_key == 'ttt_move_callback':
    self.chat.send_uni(f'move:{data['index']}', data['name'], 'tttgame')

elif hook_key == 'ttt_restart_callback':
    self.chat.send_uni(f'motion:restart', data['name'], 'tttgame')

elif hook_key == 'ttt_finish_game':
    self.chat.send_uni(f'motion:finish', data['name'], 'tttgame')