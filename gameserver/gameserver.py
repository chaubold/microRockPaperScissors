'''
Game Server that allows to add and remove players and to play a series of "Rock, Paper, Scissors" matches,
and also publishes the games in a redis queue
'''

import json
import argparse

from collections import Counter
from flask import Flask, request
from flask_autodoc import Autodoc

from game import Game

app = Flask(__name__)
doc = Autodoc(app)

game = Game()

# --------------------------------------------------------------
@app.route('/player/add', methods=['POST'])
@doc.doc()
def add_player():
    '''
    Given a json dictionary with the keys "player" and "ip",
    this registers a player to the game.

    is `markdown` supported?
    '''
    message = request.get_json(force=True)

    try:
        game.addPlayer(message['player'], message['ip'])
    except KeyError as e:
        return '{}: {}\n'.format(type(e), str(e)), 400 # return "Bad Request" because it was malformed
    except ValueError as e:
        return '{}: {}\n'.format(type(e), str(e)), 412 # return "Precondition Failed"
    
    return "Sucessfully added player " + message['player'] + '\n'

# --------------------------------------------------------------
@app.route('/player/delete', methods=['POST'])
@doc.doc()
def remove_player():
    '''
    Remove a player by providing a JSON dictionary containing the key "player".
    '''
    message = request.get_json(force=True)

    try:
        game.removePlayer(message['player'])
    except KeyError as e:
        return '{}: {}\n'.format(type(e), str(e)), 400 # return "Bad Request" because it was malformed
    except ValueError as e:
        return '{}: {}\n'.format(type(e), str(e)), 412 # return "Precondition Failed"
    
    return "Sucessfully removed player " + message['player'] + '\n'

# --------------------------------------------------------------
@app.route('/result/<int:numMatches>')
@doc.doc()
def get_result(numMatches):
    '''
    Returns the player names or "draw", with the number of times they won.
    '''
    winnerPerMatch = [game.playMatch() for _ in range(numMatches)]
    stats = Counter(winnerPerMatch)
    return json.dumps(stats.most_common())

# --------------------------------------------------------------
@app.route('/doc')
def documentation():
    ''' serve an API documentation '''
    return doc.html(title='Game Server API', author='Carsten Haubold')

# ----------------------------------------------------------------------------------------
# run server
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run the rock-paper-scissors game server.',
                                    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-p', '--port', type=int, default=6788, help='port on which to run service')
    options = parser.parse_args()

    app.run(host='0.0.0.0', port=options.port, debug=False)