from random import randint

if root == 'tttgame':
    if first != sender:
        self.proceed_command(f':sayby {first} Server Вы были приглашены {sender} на игру в крестики нолики, чтобы принять вызов введите !accept {sender}')
        if not 'tttgames' in self.any: self.any["tttgames"] = []
        self.any['tttgames'].append({ "p1": sender })
    else:
        self.callback.log('Вы не можете отправить приглашение самому себе!', 'Server')

elif root == 'accept':
    for i in range(len(self.any['tttgames'])):
        game = self.any['tttgames'][i]
        if game['p1'] == first:
            self.any['tttgames'][i]['p2'] = sender
            self.proceed_command(f':sayby {first} Server Ваше предложение принято!')
            symbol = 'XO'[randint(0,1)]
            self.any['tttgames'][i]['p1_symbol'] = symbol
            self.any['tttgames'][i]['collect_completed'] = True
            self.proceed_command(f':ssend {first} py self.callback.ui.call("pyStartMultiplayerTictactoe", "{symbol}", "{first}")')
            self.proceed_command(f':ssend {sender} py self.callback.ui.call("pyStartMultiplayerTictactoe", "{'X' if symbol == 'O' else 'O'}", "{sender}")')
            break

elif root == 'decline':
    for i in range(len(self.any['tttgames'])):
        game = self.any['tttgames'][i]
        if game['p1'] == first:
            del self.any['tttgames'][i]
            