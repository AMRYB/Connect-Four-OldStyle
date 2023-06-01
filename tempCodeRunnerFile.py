import os, time
import numpy as np
import random
import math

from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

ROWS = 6
COLUMNS = 7
EMPTY = 0
HUMAN = 1
AI = 2

MAX_SPACE_TO_WIN = 3

def create_board():
    return np.zeros((ROWS, COLUMNS), np.int8)

def is_valid_column(board, column):
    return board[0][column - 1] == EMPTY

def valid_locations(board):
    return [i for i in range(1, 8) if is_valid_column(board, i)]

def place_piece(board, player, column):
    index = column - 1
    for row in reversed(range(ROWS)):
        if board[row][index] == EMPTY:
            board[row][index] = player
            return

def clone_and_place_piece(board, player, column):
    new_board = board.copy()
    place_piece(new_board, player, column)
    return new_board

def detect_win(board, player):
    for col in range(COLUMNS - MAX_SPACE_TO_WIN):
        for row in range(ROWS):
            if all(board[row][col+i] == player for i in range(4)):
                return True
    for col in range(COLUMNS):
        for row in range(ROWS - MAX_SPACE_TO_WIN):
            if all(board[row+i][col] == player for i in range(4)):
                return True
    for col in range(COLUMNS - MAX_SPACE_TO_WIN):
        for row in range(ROWS - MAX_SPACE_TO_WIN):
            if all(board[row+i][col+i] == player for i in range(4)):
                return True
    for col in range(COLUMNS - MAX_SPACE_TO_WIN):
        for row in range(MAX_SPACE_TO_WIN, ROWS):
            if all(board[row-i][col+i] == player for i in range(4)):
                return True
    return False

def is_terminal_board(board):
    return detect_win(board, HUMAN) or detect_win(board, AI) or len(valid_locations(board)) == 0

def score(board, player):
    score = 0
    for col in range(2, 5):
        for row in range(ROWS):
            if board[row][col] == player:
                score += 3 if col == 3 else 2
    for col in range(COLUMNS - MAX_SPACE_TO_WIN):
        for row in range(ROWS):
            score += evaluate_adjacents([board[row][col+i] for i in range(4)], player)
    for col in range(COLUMNS):
        for row in range(ROWS - MAX_SPACE_TO_WIN):
            score += evaluate_adjacents([board[row+i][col] for i in range(4)], player)
    for col in range(COLUMNS - MAX_SPACE_TO_WIN):
        for row in range(ROWS - MAX_SPACE_TO_WIN):
            score += evaluate_adjacents([board[row+i][col+i] for i in range(4)], player)
    for col in range(COLUMNS - MAX_SPACE_TO_WIN):
        for row in range(MAX_SPACE_TO_WIN, ROWS):
            score += evaluate_adjacents([board[row-i][col+i] for i in range(4)], player)
    return score

def evaluate_adjacents(adjacent_pieces, player):
    opponent = HUMAN if player == AI else AI
    player_pieces = adjacent_pieces.count(player)
    empty_spaces = adjacent_pieces.count(EMPTY)
    if player_pieces == 4:
        return 99999
    elif player_pieces == 3 and empty_spaces == 1:
        return 100
    elif player_pieces == 2 and empty_spaces == 2:
        return 10
    return 0

def minimax(board, ply, alpha, beta, maxi_player):
    valid_cols = valid_locations(board)
    if ply == 0 or is_terminal_board(board):
        if detect_win(board, HUMAN):
            return (None, -1000000000)
        elif detect_win(board, AI):
            return (None, 1000000000)
        else:
            return (None, score(board, AI))
    if maxi_player:
        value = -math.inf
        col = random.choice(valid_cols)
        for c in valid_cols:
            next_board = clone_and_place_piece(board, AI, c)
            new_score = minimax(next_board, ply - 1, alpha, beta, False)[1]
            if new_score > value:
                value = new_score
                col = c
            alpha = max(alpha, value)
            if beta <= alpha:
                break
        return col, value
    else:
        value = math.inf
        col = random.choice(valid_cols)
        for c in valid_cols:
            next_board = clone_and_place_piece(board, HUMAN, c)
            new_score = minimax(next_board, ply - 1, alpha, beta, True)[1]
            if new_score < value:
                value = new_score
                col = c
            beta = min(beta, value)
            if beta <= alpha:
                break
        return col, value

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/new_game', methods=['POST'])
def new_game():
    global board, turn, is_game_won, AI_move, running_time, total_moves, minimax_times, game_mode, difficulty
    board = create_board()
    turn = random.choice([HUMAN, AI])
    is_game_won = False
    AI_move = -1
    running_time = 0
    total_moves = 0
    minimax_times = []
    data = request.get_json()
    game_mode = data.get('mode', 1)
    difficulty = data.get('difficulty', 5 if game_mode == 1 else 3)
    return jsonify({'board': board.tolist(), 'turn': turn})

@app.route('/play', methods=['POST'])
def play():
    global board, turn, is_game_won, AI_move, running_time, total_moves
    data = request.get_json()
    move = data.get('move')
    if turn == HUMAN and is_valid_column(board, move):
        place_piece(board, HUMAN, move)
        is_game_won = detect_win(board, HUMAN)
        turn = AI if not is_game_won else HUMAN
    elif turn == AI:
        start = time.time()
        AI_move, _ = minimax(board, difficulty, -math.inf, math.inf, True)
        place_piece(board, AI, AI_move)
        is_game_won = detect_win(board, AI)
        running_time = time.time() - start
        turn = HUMAN if not is_game_won else AI
    return jsonify({
        'board': board.tolist(),
        'turn': turn,
        'winner': HUMAN if detect_win(board, HUMAN) else (AI if detect_win(board, AI) else 0),
        'AI_move': AI_move,
        'game_over': is_terminal_board(board),
        'running_time': running_time
    })

if __name__ == '__main__':
    app.run(debug=True)
