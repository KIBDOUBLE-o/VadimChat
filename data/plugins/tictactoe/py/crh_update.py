if data_type == '[tttgame]':
    if self.callback.communicator.is_server:
        t = full_message.split(':')[0]
        data = full_message[(len(t)+1):]
        print(f'dasdasdasdasdad: {t} ; {data}')
        _any = self.callback.server.any
        second = ''
        symbol = ''
        game_index = 0
        for i in range(len(_any['tttgames'])):
            s = _any['tttgames'][i]['p1_symbol']
            if _any['tttgames'][i]['p1'] == sender:
                second = _any['tttgames'][i]['p2']
                symbol = s
                game_index = i
                break
            elif _any['tttgames'][i]['p2'] == sender:
                second = _any['tttgames'][i]['p1'] 
                symbol = 'O' if s == 'X' else 'X'
                game_index = i
                break
        if second != '':
            if t == 'move':
                self.callback.server.proceed_command(f':ssend {second} py self.callback.ui.call("pyMakeMove", "{data}", "{symbol}")')
            elif t == 'motion':
                if data == 'restart':
                    self.callback.server.proceed_command(f':ssend {second} py self.callback.ui.call("pyRestart")')
                elif data == 'finish':
                    self.callback.server.proceed_command(f':ssend {second} py self.callback.ui.call("pyClose")')
                    del self.callback.server.any["tttgames"][game_index]