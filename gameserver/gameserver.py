import json
from pprint import pprint
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
    return doc.html(title='Game Server API', author='Carsten Haubold')

# ----------------------------------------------------------------------------------------
# run server
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6788, debug=False)