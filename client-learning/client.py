'''
A client that is analyzing what the other players played before, 
and hence adjusts his strategy.
'''

import json
import random
import argparse
import threading
import time
import traceback
import sys

from pprint import pprint

import redis
from flask import Flask
from flask_autodoc import Autodoc

app = Flask("biasedplayer")
doc = Autodoc(app)

hands = ['rock', 'paper', 'scissors']
probabilityLock = threading.Lock()
otherPlayerProbabilities = {}

# --------------------------------------------------------------
class LearnerThread(threading.Thread):
    def __init__(self):
        super(LearnerThread, self).__init__()

    def run(self):
        r = redis.StrictRedis()
        p = r.pubsub()
        p.psubscribe('game-channel')

        otherPlayerHands = {}

        while True:
            m = p.get_message() # message is a dict!
            
            if m:
                # for k, v in m.items():
                #     if v is not None:
                #         m[k] = str(v)
                
                # a message might look like this: 
                # {
                #     "data": "b'{\"result\": \"draw\", \"otto\": \"scissors\", \"dieter\": \"scissors\"}'", 
                #     "type": "pmessage", 
                #     "channel": "b'game-channel'", 
                #     "pattern": "b'*'"
                # }
                try:
                    data = m['data']
                    pprint(data.decode())
                    dataDict = json.loads(data.decode())
                    pprint(dataDict)

                    # insert hands and update probabilities per player
                    for k, v in dataDict.items():
                        if k == 'result':
                            continue

                        previousCount = otherPlayerHands.setdefault(k, {}).get(v, 0)
                        otherPlayerHands[k][v] = previousCount + 1
                        pprint(otherPlayerHands)
                        numPlayerMatches = sum(otherPlayerHands[k].values())
                        print("{} has played {} times".format(k, numPlayerMatches))
                        
                        with probabilityLock:
                            otherPlayerProbabilities.setdefault(k, {})
                            for h in hands:
                                otherPlayerProbabilities[k][h] = float(otherPlayerHands[k].get(h, 0)) / numPlayerMatches
                            pprint(otherPlayerProbabilities)
                except:
                    print("Error while parsing message:")
                    traceback.print_exc(file=sys.stdout)

            time.sleep(0.001)

# --------------------------------------------------------------
@app.route('/hand/<opponent>')
@doc.doc()
def request_hand(opponent):
    '''
    Let the player play a hand
    '''
    print("Playing against " + opponent)
    with probabilityLock:
        if opponent in otherPlayerProbabilities.keys():
            opponentProbs = otherPlayerProbabilities[opponent]

            # we play with the inverse probabilities!
            playingProbs = [1-opponentProbs[h] for h in hands]

            p = random.random()

            if p < playingProbs[0]:
                selectedHand = 0
            if p < playingProbs[0] + playingProbs[1]:
                selectedHand = 1
            else:
                selectedHand = 2
        else:
            selectedHand = random.randint(0, 2)

    return json.dumps({'hand': hands[selectedHand]})

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

    learner = LearnerThread()
    learner.start()

    app.run(host='0.0.0.0', port=options.port, debug=False)