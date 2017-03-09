import requests
import redis
import json

class Game(object):
    hands = ['rock', 'paper', 'scissors']

    def __init__(self):
        print("Game created")

        # dictionary storing "playerName": "ip"
        self.players = {}

        # dictionary storing a list of hands per player, played in every match
        self.playerHands = {}

        # store the name of the winning player per match
        self.winnerPerMatch = []

        # connect to Redis running on default port
        self.resultPublisher = redis.StrictRedis()

    def playMatch(self):
        '''
        Play a single match by requesting a hand by both players.
        '''
        assert len(self.players) == 2, "Can only play with exactly two players!"

        # handPerPlayer is a dict of player:hand
        handPerPlayer = {}

        # get each player's hand
        for player, ip in self.players.items():
            r = requests.get("http://{ip}/hand".format(ip=ip))
            if r.status_code != 200:
                raise RuntimeError("Could not connect to ip: {}".format(ip))

            resultDict = r.json()
            hand = resultDict['hand']
            assert hand in Game.hands, "Player {} played invalid hand {}".format(player, hand)
            self.playerHands[player].append(hand)
            handPerPlayer[player] = hand

        result = self._determineWinner(handPerPlayer)

        handPerPlayer['result'] = result
        self.resultPublisher.publish('game-channel', json.dumps(handPerPlayer))

        return result

    def _determineWinner(self, handPerPlayer):
        hs = list(handPerPlayer.values())
        winnerIdx = -1
        
        if hs[0] == 'rock':
            if hs[1] == 'paper':
                winnerIdx = 1
            elif hs[1] == 'scissors':
                winnerIdx = 0
        elif hs[0] == 'paper':
            if hs[1] == 'rock':
                winnerIdx = 0
            elif hs[1] == 'scissors':
                winnerIdx = 1
        elif hs[0] == 'scissors':
            if hs[1] == 'paper':
                winnerIdx = 0
            elif hs[1] == 'rock':
                winnerIdx = 1

        if winnerIdx < 0:
            return 'draw'
        else:
            return list(handPerPlayer.keys())[winnerIdx]

    def _checkPlayerAvailable(self, ip):
        '''
        Ask a player for a hand to see whether it is reachable
        '''
        r = requests.get("http://{ip}/hand".format(ip=ip))
        if r.status_code != 200:
            raise RuntimeError("Could not connect to ip: {}".format(ip))


    def addPlayer(self, playerName, ip):
        if playerName in self.players.keys():
            raise ValueError("Player " + playerName + " already registered in game!")
        if len(self.players) == 2:
            raise ValueError("Cannot ")

        self._checkPlayerAvailable(ip)
        print("Adding player " + playerName)
        self.players[playerName] = ip
        self.playerHands[playerName] = []

    def removePlayer(self, playerName):
        if playerName not in self.players.keys():
            raise ValueError("Player " + playerName + " not registered in game!")

        print("Removing player " + playerName)
        del self.players[playerName]
        del self.playerHands[playerName]

    def removeAllPlayers(self):
        ''' reset everything to an empty game '''
        self.players = {}
        self.playerHands = {}
        self.winnerPerMatch = []

