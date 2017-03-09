import argparse
import sys
import signal
import subprocess
import json
import time
import requests
from pprint import pprint

from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import *

import redis

class RedisListenerThread(QThread):
    messageSignal = pyqtSignal(str)

    def __init__(self, parent=None):
        super(RedisListenerThread, self).__init__(parent)

    def run(self):
        r = redis.StrictRedis()
        p = r.pubsub()
        p.psubscribe('*')

        while True:
            m = p.get_message() # message is a dict!
            
            if m:
                for k, v in m.items():
                    if v is not None:
                        m[k] = str(v)
                
                self.messageSignal.emit("Redis listener got:" + json.dumps(m))

            time.sleep(0.01)

class ServiceRunnerThread(QThread):
    messageSignal = pyqtSignal(str)

    def __init__(self, pythonFile, port, parent=None):
        super(ServiceRunnerThread, self).__init__(parent)
        self.pythonFile = pythonFile
        self.port = port

    def run(self):
        self.messageSignal.emit("Starting {} on port {}".format(self.pythonFile, self.port))
        subprocess.check_call(["python", self.pythonFile, "-p", str(self.port)])

class MyWindow(QtWidgets.QMainWindow):
    def __init__(self, options):
        '''
        Init the frame, and passing in the options object as returned from argparse
        '''
        super(MyWindow, self).__init__()
        uic.loadUi('viewer.ui', self)
        
        # store initial values, if given
        if options.game_server_ip is not None:
            self.gameserverIp_txt.setText(options.game_server_ip)

        if options.player1_name is not None:
            self.player1Name_txt.setText(options.player1_name)
        if options.player1_ip is not None:
            self.player1Ip_txt.setText(options.player1_ip)

        if options.player2_name is not None:
            self.player2Name_txt.setText(options.player2_name)
        if options.player2_ip is not None:
            self.player2Ip_txt.setText(options.player2_ip)

        # register event handlers
        self.play_btn.clicked.connect(self._playButtonClicked)

        # start thread for redis messages
        self.redisListenerThread = RedisListenerThread()
        self.redisListenerThread.messageSignal.connect(self._appendToLog)
        self.redisListenerThread.start()

        # no game threads running yet:
        self.player1Thread = None
        self.player2Thread = None
        self.gameServerThread = None

        self.show()

    def closeEvent(self, event):
        if self.redisListenerThread:
            self.redisListenerThread.quit()

        if self.player1Thread:
            self.player1Thread.quit()

        if self.player2Thread:
            self.player2Thread.quit()

        if self.gameServerThread:
            self.gameServerThread.quit()
        event.accept()

    def _appendToLog(self, message):
        self.log_display.append(message)

    def _playButtonClicked(self):
        # read important values and do something
        self.statusbar.showMessage("play clicked!", 1000)
        # self.player1Thread = ServiceRunnerThread("../client-random/client.py", 6789)
        # self.player1Thread.messageSignal.connect(self._appendToLog)
        # self.player1Thread.start()

        # self.player2Thread = ServiceRunnerThread("../client-random/client.py", 6790)
        # self.player2Thread.messageSignal.connect(self._appendToLog)
        # self.player2Thread.start()

        # self.gameServerThread = ServiceRunnerThread("../gameserver/gameserver.py", 9876)
        # self.gameServerThread.messageSignal.connect(self._appendToLog)
        # self.gameServerThread.start()
        # self.statusbar.showMessage("servers started!", 1000)

        # timer = QTimer(self)
        # timer.timeout.connect(self._connectPlayers)
        # timer.start(1000)

        self._connectPlayers()

        r = requests.get("http://{ip}/result/{num}".format(ip=self.gameserverIp_txt.text(),
                                                            num=self.numMatches_spin.value()))
        r.raise_for_status()
        # resultDict = r.json()
        self.log_display.append('<span style=" color:#ff0000;">Who won how often? ' + r.text + '</span>')


    def _connectPlayers(self):
        # clear current gameserver:
        r = requests.get("http://{ip}/player/removeall".format(ip=self.gameserverIp_txt.text()))
        r.raise_for_status()

        # connect players
        payload = {"player": self.player1Name_txt.text(), "ip": self.player1Ip_txt.text()}
        r = requests.post("http://{ip}/player/add".format(ip=self.gameserverIp_txt.text()), data=json.dumps(payload))
        r.raise_for_status()

        payload = {"player": self.player2Name_txt.text(), "ip": self.player2Ip_txt.text()}
        r = requests.post("http://{ip}/player/add".format(ip=self.gameserverIp_txt.text()), data=json.dumps(payload))
        r.raise_for_status()

        self.statusbar.showMessage("players connected!", 1000)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run the viewer that connects to game and player on startup if given',
                                    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--game-server-ip', type=str, default=None, help='<ip>:<port> on which the game service is running')
    
    parser.add_argument('--player1-name', type=str, default=None, help='player 1 name')
    parser.add_argument('--player1-ip', type=str, default=None, help='player 1 ip:port address')

    parser.add_argument('--player2-name', type=str, default=None, help='player 2 name')
    parser.add_argument('--player2-ip', type=str, default=None, help='player 2 ip:port address')
    
    options = parser.parse_args()
    app = QtWidgets.QApplication(sys.argv)

    # set CTRL+C behave as its default: quit!
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    window = MyWindow(options)
    sys.exit(app.exec_())

    