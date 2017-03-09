'''
A client that is very biased
'''

import json
import random
import argparse
import numpy as np

from flask import Flask
from flask_autodoc import Autodoc

app = Flask("biasedplayer")
doc = Autodoc(app)

hands = ['rock', 'paper', 'scissors']
preferredHand = random.randint(0, 2)
print("Player will always play {}".format(hands[preferredHand]))

# --------------------------------------------------------------
@app.route('/hand/<opponent>')
@doc.doc()
def request_hand(opponent):
    '''
    Let the player play a hand
    '''

    return json.dumps({'hand': hands[preferredHand]})

# --------------------------------------------------------------
@app.route('/doc')
def documentation():
    ''' serve an API documentation '''
    return doc.html(title='Biased Player API', author='Carsten Haubold')

# ----------------------------------------------------------------------------------------
# run server
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run a player with a very biased strategy',
                                    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-p', '--port', type=int, default=6789, help='port on which to run service')
    options = parser.parse_args()

    app.run(host='0.0.0.0', port=options.port, debug=False)