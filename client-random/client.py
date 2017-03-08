import json
import random
import argparse

from flask import Flask
from flask_autodoc import Autodoc

app = Flask("randomplayer")
doc = Autodoc(app)

hands = ['rock', 'paper', 'scissors']

# --------------------------------------------------------------
@app.route('/hand')
@doc.doc()
def request_hand():
    '''
    Let the player play a hand
    '''
    return json.dumps({'hand': hands[random.randint(0,2)]})

# --------------------------------------------------------------
@app.route('/doc')
def documentation():
    return doc.html(title='Random Player API', author='Carsten Haubold')

# ----------------------------------------------------------------------------------------
# run server
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run a player with a random strategy',
                                    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-p', '--port', type=int, default=6789, help='port on which to run service')
    options = parser.parse_args()

    app.run(host='0.0.0.0', port=options.port, debug=False)