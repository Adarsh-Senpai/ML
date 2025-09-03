from flask import Flask, render_template_string, request, jsonify
import random
import streamlit as st

st.title("My ML App")
st.write("Hello! This is running on Streamlit Cloud 🚀")




app = Flask(__name__)

# Game state - using simple variables instead of class instances
board = [0] * 9
current_player = 1
done = False
winner = None
round_wins = 0
round_losses = 0
round_draws = 0
player_match_wins = 0
ai_match_wins = 0
match_over = False

def handler(request, response):
    # Example: simple ML placeholder
    return response.json({"message": "ML model is running!"})


def reset_game():
    global board, current_player, done, winner
    board = [0] * 9
    current_player = 1
    done = False
    winner = None

def reset_match():
    global board, current_player, done, winner, round_wins, round_losses, round_draws, player_match_wins, ai_match_wins, match_over
    board = [0] * 9
    current_player = 1
    done = False
    winner = None
    round_wins = 0
    round_losses = 0
    round_draws = 0
    player_match_wins = 0
    ai_match_wins = 0
    match_over = False

def check_winner(board_state):
    wins = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],
        [0, 3, 6], [1, 4, 7], [2, 5, 8],
        [0, 4, 8], [2, 4, 6]
    ]
    for line in wins:
        if board_state[line[0]] != 0 and board_state[line[0]] == board_state[line[1]] == board_state[line[2]]:
            return board_state[line[0]]
    if 0 not in board_state:
        return 0
    return None

def make_move(pos, player):
    global board, done, winner, current_player, round_wins, round_losses, round_draws, player_match_wins, ai_match_wins, match_over
    
    if not done and not match_over and board[pos] == 0:
        board[pos] = player
        winner = check_winner(board)
        if winner is not None:
            done = True
            if winner == 1:
                round_wins += 1
                player_match_wins += 1
            elif winner == -1:
                round_losses += 1
                ai_match_wins += 1
            else:
                round_draws += 1
            if player_match_wins >= 3 or ai_match_wins >= 3:
                match_over = True
        else:
            current_player = -player
        return True
    return False

def ai_choose_move():
    available = [i for i, v in enumerate(board) if v == 0]
    
    # Try to win
    for move in available:
        test_board = board[:]
        test_board[move] = -1
        if check_winner(test_board) == -1:
            return move
    
    # Block player
    for move in available:
        test_board = board[:]
        test_board[move] = 1
        if check_winner(test_board) == 1:
            return move
    
    # Take center
    if 4 in available:
        return 4
    
    # Take corners
    corners = [0, 2, 6, 8]
    available_corners = [m for m in available if m in corners]
    if available_corners:
        return random.choice(available_corners)
    
    return random.choice(available)

@app.route('/')
def home():
    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tic Tac Toe AI</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
            background: #f0f2f5;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            text-align: center;
            max-width: 400px;
        }
        h1 { color: #333; margin-bottom: 10px; }
        .subtitle { color: #666; margin-bottom: 20px; }
        .match-info {
            background: #f8f9fa;
            padding: 12px;
            border-radius: 8px;
            margin: 20px 0;
            font-weight: bold;
        }
        .board {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 8px;
            margin: 25px auto;
            max-width: 300px;
        }
        .cell {
            width: 80px;
            height: 80px;
            background: #f8f9fa;
            border: 2px solid #e9ecef;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 28px;
            font-weight: bold;
            cursor: pointer;
            border-radius: 8px;
            transition: all 0.2s;
        }
        .cell:hover { background: #e9ecef; transform: scale(1.05); }
        .cell.x { color: #dc3545; }
        .cell.o { color: #007bff; }
        .status {
            margin: 20px 0;
            font-size: 18px;
            font-weight: bold;
            min-height: 25px;
        }
        .scores { margin: 15px 0; color: #666; }
        button {
            background: #007bff;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            font-weight: bold;
            transition: background 0.2s;
        }
        button:hover { background: #0056b3; }
        .winner { color: #28a745; }
        .loser { color: #dc3545; }
        .thinking { color: #17a2b8; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎮 Tic Tac Toe AI</h1>
        <p class="subtitle">Fast Q-Learning Algorithm</p>
        
        <div class="match-info">
            <div>🏆 Best of 3 Matches</div>
            <div id="matchScore">Player: 0 | AI: 0</div>
        </div>
        
        <div class="board" id="board"></div>
        
        <div class="status" id="status">Your turn! Click a cell</div>
        <div class="scores" id="scores">Wins: 0 | Losses: 0 | Draws: 0</div>
        
        <button id="resetBtn">New Round</button>
    </div>

    <script>
        const boardEl = document.getElementById('board');
        const statusEl = document.getElementById('status');
        const scoresEl = document.getElementById('scores');
        const matchScoreEl = document.getElementById('matchScore');
        const resetBtn = document.getElementById('resetBtn');
        
        let board = Array(9).fill(0);
        let gameOver = false;
        let matchOver = false;

        function renderBoard() {
            boardEl.innerHTML = '';
            board.forEach((cell, i) => {
                const cellEl = document.createElement('div');
                cellEl.className = 'cell';
                
                if (cell === 1) {
                    cellEl.textContent = 'X';
                    cellEl.classList.add('x');
                } else if (cell === -1) {
                    cellEl.textContent = 'O';
                    cellEl.classList.add('o');
                } else {
                    cellEl.addEventListener('click', () => handleCellClick(i));
                }
                
                boardEl.appendChild(cellEl);
            });
        }

        async function handleCellClick(index) {
            if (gameOver || matchOver || board[index] !== 0) return;
            
            try {
                const response = await fetch('/move', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ position: index, player: 1 })
                });
                const data = await response.json();
                updateGameState(data);
            } catch (error) {
                console.error('Move error:', error);
            }
        }

        async function makeAIMove() {
            if (gameOver || matchOver) return;
            
            statusEl.innerHTML = '<span class="thinking">🤖 AI thinking...</span>';
            
            setTimeout(async () => {
                try {
                    const response = await fetch('/ai_move', { method: 'POST' });
                    const data = await response.json();
                    updateGameState(data);
                } catch (error) {
                    console.error('AI move error:', error);
                }
            }, 800);
        }

        function updateGameState(data) {
            board = data.board;
            gameOver = data.game_over;
            matchOver = data.match_over;
            
            renderBoard();
            updateScores(data);
            updateStatus(data);
            
            if (!gameOver && !matchOver && data.current_player === -1) {
                setTimeout(makeAIMove, 500);
            }
        }

        function updateScores(data) {
            scoresEl.textContent = `Wins: ${data.round_wins} | Losses: ${data.round_losses} | Draws: ${data.round_draws}`;
            matchScoreEl.textContent = `Player: ${data.player_match_wins} | AI: ${data.ai_match_wins}`;
        }

        function updateStatus(data) {
            if (data.match_over) {
                if (data.player_match_wins >= 3) {
                    statusEl.innerHTML = '<span class="winner">🎉 You won the match!</span>';
                } else {
                    statusEl.innerHTML = '<span class="loser">🤖 AI won the match!</span>';
                }
                resetBtn.textContent = 'New Match';
            } else if (data.game_over) {
                if (data.winner === 1) {
                    statusEl.innerHTML = '<span class="winner">✅ You win this round!</span>';
                } else if (data.winner === -1) {
                    statusEl.innerHTML = '<span class="loser">🤖 AI wins this round!</span>';
                } else {
                    statusEl.textContent = '🤝 Draw!';
                }
                resetBtn.textContent = 'Next Round';
            } else {
                statusEl.textContent = data.current_player === 1 ? 'Your turn! Click a cell' : '🤖 AI turn';
                resetBtn.textContent = 'New Round';
            }
        }

        resetBtn.onclick = async () => {
            const endpoint = matchOver ? '/reset_match' : '/reset_round';
            try {
                const response = await fetch(endpoint, { method: 'POST' });
                const data = await response.json();
                board = data.board;
                gameOver = false;
                matchOver = data.match_over || false;
                renderBoard();
                updateScores(data);
                statusEl.textContent = 'Your turn! Click a cell';
                resetBtn.textContent = 'New Round';
            } catch (error) {
                console.error('Reset error:', error);
            }
        };

        renderBoard();
    </script>
</body>
</html>
    ''')

@app.route('/move', methods=['POST'])
def move():
    try:
        data = request.get_json()
        pos = data.get('position')
        player = data.get('player')
        
        if current_player == player:
            make_move(pos, player)
        
        return jsonify({
            'board': board,
            'current_player': current_player,
            'game_over': done,
            'winner': winner,
            'match_over': match_over,
            'round_wins': round_wins,
            'round_losses': round_losses,
            'round_draws': round_draws,
            'player_match_wins': player_match_wins,
            'ai_match_wins': ai_match_wins
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/ai_move', methods=['POST'])
def ai_move():
    try:
        if not done and not match_over and current_player == -1:
            available = [i for i, v in enumerate(board) if v == 0]
            if available:
                pos = ai_choose_move()
                make_move(pos, -1)
        
        return jsonify({
            'board': board,
            'current_player': current_player,
            'game_over': done,
            'winner': winner,
            'match_over': match_over,
            'round_wins': round_wins,
            'round_losses': round_losses,
            'round_draws': round_draws,
            'player_match_wins': player_match_wins,
            'ai_match_wins': ai_match_wins
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/reset_round', methods=['POST'])
def reset_round():
    try:
        reset_game()
        return jsonify({
            'board': board,
            'current_player': current_player,
            'game_over': done,
            'winner': winner,
            'match_over': match_over,
            'round_wins': round_wins,
            'round_losses': round_losses,
            'round_draws': round_draws,
            'player_match_wins': player_match_wins,
            'ai_match_wins': ai_match_wins
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/reset_match', methods=['POST'])
def reset_match_route():
    try:
        reset_match()
        return jsonify({
            'board': board,
            'current_player': current_player,
            'game_over': done,
            'winner': winner,
            'match_over': match_over,
            'round_wins': round_wins,
            'round_losses': round_losses,
            'round_draws': round_draws,
            'player_match_wins': player_match_wins,
            'ai_match_wins': ai_match_wins
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Vercel entry point
app = app
