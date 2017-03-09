# Rock-Paper-Scissors using Flask microservices

Used to understand the concepts and have some fun :)

## Installing required packages (with conda)

This is Python 3 only!

* Flask: `pip install flask`
* Autodoc (*will probably replaced in the future*): `pip install Flask-Autodoc`
* qt5 and pyqt for the viewer: `conda install pyqt==5.6.0`

You also need to run a redis server on the default port which is used to communicate the results.
Install docker and run the latest redis in a linux container as follows: 
    
    docker run -d -p 6379:6379 --name redis bitnami/redis:latest

Where the parameters mean:
* `-d` = run as daemon
* `-p` port:port = forward this specific port from the container to localhost (6379 is redis default)
* `--name` = provide a name for the container that can be used with start/stop,...

## Running server and playing matches

Start server and two players (`client-random`, `client-biased` and `client-learning` are available):

```sh
# best in seperate terminals, or put an "&" at the end of every line
python gameserver/gameserver.py -p 9876
python client-random/client.py -p 6789
python client-random/client.py -p 6790
```

To see the API any of the clients offer, navigate your webbrowser to `localhost:port/doc`.

Tell the server which players are playing:

```sh
curl -i -d '{"player":"joe", "ip":"0.0.0.0:6789"}' localhost:9876/player/add
curl -i -d '{"player":"paul", "ip":"0.0.0.0:6790"}' localhost:9876/player/add
```

Play 100 matches:

```sh
curl -i localhost:9876/result/100
```

Or fire up a viewer that will talk to the gameserver and connect the players:

```sh
python viewer.py --game-server-ip 0.0.0.0:9876 --player1-name joe --player1-ip 0.0.0.0:6789 --player2-name paul --player2-ip 0.0.0.0:6790
```
