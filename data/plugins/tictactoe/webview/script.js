// ---------------------------
// CORE ENGINE (логика игры)
// ---------------------------
class TicTacToeEngine {
    constructor(onUpdate) {
        this.onUpdate = onUpdate; // callback → UI обновление/сообщения
        this.reset(false);
    }

    reset(multiplayer = false, mySymbol = 'X', myName='') {
        this.board = Array(9).fill('');
        this.currentPlayer = 'X';
        this.gameActive = true;
        this.isMultiplayer = multiplayer;
        this.mySymbol = mySymbol;
        this.myName = myName;

        this.onUpdate({ type: "reset", board: this.board });
        this.onUpdate({ type: "info", text: `Ходят: ${this.currentPlayer}` });
        this.onUpdate({ type: "me", text: `Вы играете: ${this.mySymbol} `});

        if (multiplayer) {
            //window.pywebview.api.send_message(JSON.stringify({
            //    event: "ttt_start"
            //}));
        }
    }

    makeMove(index, symbol) {
        if (!this.gameActive) return false;
        if (this.board[index] !== "") return false;
        if (symbol !== this.currentPlayer) return false;

        this.board[index] = symbol;
        this.onUpdate({ type: "update_cell", index, symbol });

        // Проверка победы
        if (this.checkWin(symbol)) {
            this.gameActive = false;
            this.onUpdate({ type: "game_end", result: `${symbol}`, text: `Победил: ${symbol}! 🎉` });
            return true;
        }

        // Ничья
        if (!this.board.includes("")) {
            this.gameActive = false;
            this.onUpdate({ type: "game_end", result: "draw", text: "Ничья! 🤝" });
            return true;
        }

        // Меняем ход
        this.currentPlayer = this.currentPlayer === 'X' ? 'O' : 'X';
        this.onUpdate({ type: "info", text: `Ходят: ${this.currentPlayer}` });

        return true;
    }

    // Для одиночной игры — ход компьютера
    computerMove() {
        if (!this.gameActive || this.isMultiplayer) return;
        let empty = this.board.map((v, i) => v === '' ? i : null).filter(i => i !== null);
        if (empty.length === 0) return;

        let move = empty[Math.floor(Math.random() * empty.length)];
        this.makeMove(move, 'O');
    }

    checkWin(symbol) {
        const winPatterns = [
            [0,1,2],[3,4,5],[6,7,8],
            [0,3,6],[1,4,7],[2,5,8],
            [0,4,8],[2,4,6]
        ];
        return winPatterns.some(p => 
            p.every(i => this.board[i] === symbol)
        );
    }
}


// ---------------------------
// UI слой — только отображение
// ---------------------------
const UI = {
    boardEl: document.getElementById('tictactoeBoard'),
    gameEl: document.getElementById('tictactoeGame'),
    infoEl: document.getElementById('tictactoeInfo'),
    meEl: document.getElementById('tictactoeMe'),

    resetBoard() {
        [...this.boardEl.querySelectorAll('.tictactoe-cell')].forEach(c => {
            c.textContent = "";
            c.className = "tictactoe-cell";
            c.style = "";
        });
    },

    updateCell(index, symbol) {
        let cell = this.boardEl.querySelector(`[data-index="${index}"]`);
        cell.textContent = symbol;
        cell.className = `tictactoe-cell ${symbol}`;
    },

    highlight(pattern) {
        pattern.forEach(i => {
            let cell = this.boardEl.querySelector(`[data-index="${i}"]`);
            cell.style.background = "rgba(0, 122, 204, 0.3)";
        });
    },

    setInfo(text) {
        this.infoEl.textContent = text;
    },

    setMe(text) {
        this.meEl.textContent = text;
    },

    show() { this.gameEl.style.display = "block"; },
    hide() { this.gameEl.style.display = "none"; }
};


// ---------------------------
// ИНИЦИАЛИЗАЦИЯ ИГРОВОГО ДВИЖКА
// ---------------------------
const engine = new TicTacToeEngine((event) => {
    switch (event.type) {
        case "reset":
            UI.resetBoard();
            break;
        case "update_cell":
            UI.updateCell(event.index, event.symbol);
            break;
        case "info":
            UI.setInfo(event.text);
            break;
        case "me":
            UI.setMe(event.text);
            break;
        case "game_end":
            UI.setInfo(event.text);
            break;
    }
});


// ---------------------------
// UI ОБРАБОТЧИКИ
// ---------------------------
document.getElementById('tictactoeBtn').onclick = () => {
    UI.show();
    engine.reset(false);
};

document.getElementById('restartTictactoe').onclick = () => {
    if (engine.isMultiplayer) {
        window.pywebview.api.hook('ttt_restart_callback', {
            name: engine.myName
        });
    }
    engine.reset(engine.isMultiplayer, engine.mySymbol, engine.myName);
};

document.getElementById('closeTictactoe').onclick = () => {
    if (engine.isMultiplayer) {
        window.pywebview.api.hook('ttt_finish_game', {
            name: engine.myName
        })
    }
    UI.hide();
};

UI.boardEl.addEventListener("click", e => {
    if (!e.target.classList.contains("tictactoe-cell")) return;

    let index = +e.target.dataset.index;

    // В мультиплеере ход может быть только своим символом
    let symbol = engine.isMultiplayer ? engine.mySymbol : engine.currentPlayer;

    if (engine.makeMove(index, symbol)) {
        // Отправляем ход Python
        if (engine.isMultiplayer || true) {
            window.pywebview.api.hook('ttt_move_callback', {
                index: index,
                name: engine.myName
            });
        }

        // В одиночном режиме ходит компьютер
        if (!engine.isMultiplayer) {
            setTimeout(() => engine.computerMove(), 300);
        }
    }
});


// --------------------------------------------
// ВЫЗОВЫ ИЗ PYTHON (API для мультиплеера)
// --------------------------------------------
window.pyStartMultiplayerTictactoe = function(symbol, name) {
    UI.show();
    engine.reset(true, symbol, name);
};

window.pyMakeMove = function(index, symbol) {
    engine.makeMove(index, symbol);
};

window.pyRestart = function() {
    engine.reset(engine.isMultiplayer, engine.mySymbol, engine.myName);
};

window.pyClose = function() {
    window.pywebview.api.hook('ttt_finish_game', {
        name: engine.myName
    })
    UI.hide();
};
