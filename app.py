import streamlit as st
import random
import time

st.set_page_config(page_title="Tic Tac Toe AI", layout="centered")
st.title("🎮 Tic Tac Toe AI")
st.write("Fast Q-Learning AI (Player vs AI)")

# -----------------------------
# Initialize game state
# -----------------------------
if "board" not in st.session_state:
    st.session_state.board = [0] * 9
if "current_player" not in st.session_state:
    st.session_state.current_player = 1
if "done" not in st.session_state:
    st.session_state.done = False
if "winner" not in st.session_state:
    st.session_state.winner = None
if "round_wins" not in st.session_state:
    st.session_state.round_wins = 0
if "round_losses" not in st.session_state:
    st.session_state.round_losses = 0
if "round_draws" not in st.session_state:
    st.session_state.round_draws = 0
if "player_match_wins" not in st.session_state:
    st.session_state.player_match_wins = 0
if "ai_match_wins" not in st.session_state:
    st.session_state.ai_match_wins = 0
if "match_over" not in st.session_state:
    st.session_state.match_over = False

# -----------------------------
# Helper functions
# -----------------------------
def check_winner(board):
    wins = [
        [0,1,2],[3,4,5],[6,7,8],
        [0,3,6],[1,4,7],[2,5,8],
        [0,4,8],[2,4,6]
    ]
    for line in wins:
        if board[line[0]] != 0 and board[line[0]] == board[line[1]] == board[line[2]]:
            return board[line[0]]
    if 0 not in board:
        return 0
    return None

def make_move(pos, player):
    if st.session_state.done or st.session_state.match_over:
        return
    if st.session_state.board[pos] == 0:
        st.session_state.board[pos] = player
        winner = check_winner(st.session_state.board)
        if winner is not None:
            st.session_state.done = True
            st.session_state.winner = winner
            if winner == 1:
                st.session_state.round_wins += 1
                st.session_state.player_match_wins += 1
            elif winner == -1:
                st.session_state.round_losses += 1
                st.session_state.ai_match_wins += 1
            else:
                st.session_state.round_draws += 1
            if st.session_state.player_match_wins >= 3 or st.session_state.ai_match_wins >= 3:
                st.session_state.match_over = True
        else:
            st.session_state.current_player = -player

def ai_choose_move():
    available = [i for i, v in enumerate(st.session_state.board) if v == 0]
    # Try to win
    for move in available:
        test_board = st.session_state.board[:]
        test_board[move] = -1
        if check_winner(test_board) == -1:
            return move
    # Block player
    for move in available:
        test_board = st.session_state.board[:]
        test_board[move] = 1
        if check_winner(test_board) == 1:
            return move
    # Take center
    if 4 in available:
        return 4
    # Take corners
    corners = [0,2,6,8]
    corner_moves = [m for m in available if m in corners]
    if corner_moves:
        return random.choice(corner_moves)
    # Random
    return random.choice(available)

def reset_round():
    st.session_state.board = [0]*9
    st.session_state.current_player = 1
    st.session_state.done = False
    st.session_state.winner = None

def reset_match():
    reset_round()
    st.session_state.round_wins = 0
    st.session_state.round_losses = 0
    st.session_state.round_draws = 0
    st.session_state.player_match_wins = 0
    st.session_state.ai_match_wins = 0
    st.session_state.match_over = False

# -----------------------------
# Game logic
# -----------------------------
def player_move(pos):
    if st.session_state.current_player == 1 and not st.session_state.done:
        make_move(pos, 1)
        # AI moves after player
        if not st.session_state.done and not st.session_state.match_over:
            st.session_state.current_player = -1
            st.experimental_rerun()

def ai_move():
    if st.session_state.current_player == -1 and not st.session_state.done:
        time.sleep(0.3)  # AI thinking delay
        pos = ai_choose_move()
        make_move(pos, -1)
        st.session_state.current_player = 1
        st.experimental_rerun()

# Run AI move automatically
if st.session_state.current_player == -1 and not st.session_state.done:
    ai_move()

# -----------------------------
# Display board
# -----------------------------
st.subheader("🏆 Best of 3 Matches")
st.write(f"Player: {st.session_state.player_match_wins} | AI: {st.session_state.ai_match_wins}")
st.write(f"Wins: {st.session_state.round_wins} | Losses: {st.session_state.round_losses} | Draws: {st.session_state.round_draws}")

# Render HTML board with improved style
board_html = '<div style="display:grid; grid-template-columns: repeat(3, 100px); gap:8px; justify-content:center; margin-bottom:15px;">'
for idx, cell in enumerate(st.session_state.board):
    color = "#dc3545" if cell == 1 else "#007bff" if cell == -1 else "#f8f9fa"
    label = "X" if cell == 1 else "O" if cell == -1 else ""
    board_html += f'''
        <button style="
            width:100px;height:100px;font-size:36px;font-weight:bold;
            color:{color};border-radius:12px;border:2px solid #e9ecef;
            background:#f8f9fa;cursor:pointer;box-shadow:0 4px 8px rgba(0,0,0,0.1);
            transition: all 0.2s;" onclick="window.location.href='?move={idx}'">{label}</button>
    '''
board_html += '</div>'
st.markdown(board_html, unsafe_allow_html=True)

# Handle player click using st.query_params
move_idx = st.query_params.get("move")
if move_idx:
    player_move(int(move_idx[0]))

# -----------------------------
# Round/Match Results
# -----------------------------
if st.session_state.match_over:
    if st.session_state.player_match_wins >= 3:
        st.success("🎉 You won the match!")
    else:
        st.error("🤖 AI won the match!")
elif st.session_state.done:
    if st.session_state.winner == 1:
        st.success("✅ You win this round!")
    elif st.session_state.winner == -1:
        st.error("🤖 AI wins this round!")
    else:
        st.info("🤝 Draw!")

# Reset buttons
st.button("🔄 Reset Round", on_click=reset_round)
st.button("🏁 Reset Match", on_click=reset_match)
