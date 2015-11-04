# sg-dashboard
A dashboard to visualize game data.

## Requires

sudo apt-get install build-essential libssl-dev libffi-dev python3-dev

pip install flask flask-sqlalchemy flask-auth flask-api pyOpenSSL cryptography passlib sqlalchemy-migrate

## Try it out

First, remember to activate the virtualenv, if any.
 
Run the server:

$ python dashboard/run.py

Visit the dashboard: http://localhost:5001/events

See events commited in the test session by filling in the value "aaaa" and clicking in the link.