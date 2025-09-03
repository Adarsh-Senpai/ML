import streamlit as st
import random

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
# Game UI
# -----------------------------
st.subheader("Best of 3 Matches")
st.write(f"🏆 Player: {st.session_state.player_match_wins} | AI: {st.session_state.ai_match_wins}")
st.write(f"Wins: {st.session_state.round_wins} | Losses: {st.session_state.round_losses} | Draws: {st.session_state.round_draws}")

# Custom CSS for board
st.markdown("""
<style>
.board-cell {
    width: 80px;
    height: 80px;
    display: inline-flex;
    justify-content: center;
    align-items: center;
    font-size: 32px;
    font-weight: bold;
    margin: 2px;
    border-radius: 8px;
    cursor: pointer;
    transition: 0.2s;
}
.board-cell:hover {
    background-color: #e9ecef;
}
.cell-x {
    color: #dc3545;
}
.cell-o {
    color: #007bff;
}
</style>
""", unsafe_allow_html=True)

# Display board as grid
for i in range(3):
    cols = st.columns(3)
    for j, col in enumerate(cols):
        idx = i*3 + j
        label = ""
        cell_class = ""
        if st.session_state.board[idx] == 1:
            label = "X"
            cell_class = "cell-x"
        elif st.session_state.board[idx] == -1:
            label = "O"
            cell_class = "cell-o"
        html_button = f'<div class="board-cell {cell_class}">{label}</div>'
        if col.button(label, key=idx):
            if st.session_state.board[idx] == 0:
                make_move(idx, 1)
                # AI move
                if not st.session_state.done and not st.session_state.match_over:
                    ai_pos = ai_choose_move()
                    make_move(ai_pos, -1)

# Display round/match results
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
