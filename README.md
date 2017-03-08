# Rock-Paper-Scissors using Flask microservices

Used to understand the concepts and have some fun :)

## Installing required packages (with conda)

This is Python 3 only!

* Flask: `pip install flask`
* Autodoc (*will probably replaced in the future*): `pip install Flask-Autodoc`
* qt5 and pyqt: `conda install pyqt==5.6.0`

## Running server and playing matches

Start server and two players:

```sh
# best in seperate terminals, or put an "&" at the end of every line
python gameserver/gameserver.py -p 9876
python client-random/client.py -p 6789
python client-random/client.py -p 6790
```

Tell the server which players are playing:

```sh
curl -i -d '{"player":"joe", "ip":"0.0.0.0:6789"}' localhost:9876/player/add
curl -i -d '{"player":"paul", "ip":"0.0.0.0:6790"}' localhost:9876/player/add
```

Play 100 matches

```sh
curl -i localhost:9876/result/100
```

