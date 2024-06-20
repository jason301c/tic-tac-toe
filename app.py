from flask import Flask, render_template, request, jsonify
import random
import string
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta

# Initialization and global variables
app = Flask(__name__)
games = {}                          # Dict of all games
scheduler = BackgroundScheduler()
scheduler.start()


# Helper functions
def generate_game_id():
    """
    :return: 6 letter unique alphanumeric string
    """
    while True:
        game_id = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
        if game_id not in games:
            return game_id


def check_winner(board, player):
    """
    :param board: Game's board (list of strings with size 9)
    :param player: Player's character (X or O)
    :return: Boole, whether the player is indeed the winner
    """
    win_conditions = [
        [board[0], board[1], board[2]],
        [board[3], board[4], board[5]],
        [board[6], board[7], board[8]],
        [board[0], board[3], board[6]],
        [board[1], board[4], board[7]],
        [board[2], board[5], board[8]],
        [board[0], board[4], board[8]],
        [board[2], board[4], board[6]]
    ]
    return [player, player, player] in win_conditions

def delete_game(game_id):
    """
    Delete game by game ID
    """
    if game_id in games:
        del games[game_id]
        print(f"Game {game_id} deleted.")
def cleanup_games():
    now = datetime.now()
    for game_id in list(games.keys()):
        game = games[game_id]
        if (game.get('finished') and game.get('end_time') < now - timedelta(minutes=5)) or \
           (game.get('last_activity') < now - timedelta(minutes=10)):
            delete_game(game_id)

scheduler.add_job(cleanup_games, 'interval', minutes=5)

# Flask routing
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/create-game', methods=['POST'])
def create_game():
    """
    Initializes a game with a random game-id
    """
    game_id = generate_game_id()
    games[game_id] = {'board': [''] * 9, 'currentPlayer': 'X', 'finished': False, 'last_activity': datetime.now()}
    print(f"Game {game_id} created.")
    return jsonify({'status': 'Game created!', 'gameId': game_id})


@app.route('/game/<game_id>', methods=['GET'])
def game(game_id):
    """
    Joins a game with game id as URl
    """
    if game_id in games:
        return jsonify({'status': 'Game joined', 'game': games[game_id]})
    else:
        return jsonify({'status': 'Game not found'}), 404


@app.route('/make-move', methods=['POST'])
def make_move():
    """
    Making move by POST
    """
    game_id = request.json.get('gameId')
    index = request.json.get('index')
    player = request.json.get('player')

    if game_id in games:
        game = games[game_id]
        # Handles win checking
        if game['board'][index] == '' and game['currentPlayer'] == player:
            game['board'][index] = player
            game['last_activity'] = datetime.now()
            if check_winner(game['board'], player):
                game['finished'] = True
                game['end_time'] = datetime.now()
                return jsonify({'status': 'Player won', 'game': game})
            elif '' not in game['board']:
                game['finished'] = True
                game['end_time'] = datetime.now()
                return jsonify({'status': 'Draw', 'game': game})
            else:
                game['currentPlayer'] = 'O' if player == 'X' else 'X'
                return jsonify({'status': 'Move made', 'game': game})
        else:
            return jsonify({'status': 'Invalid move or wrong player turn'}), 400
    else:
        return jsonify({'status': 'Game not found'}), 404


if __name__ == '__main__':
    try:
        app.run(debug=True)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
