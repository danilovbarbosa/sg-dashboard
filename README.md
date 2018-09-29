# sg-dashboard
A dashboard to visualize game data.

## Requires for Dev

sudo apt-get install build-essential libssl-dev libffi-dev python3-dev 

sudo apt-get install git python-pip make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev curl

## Create an environment (Linux)

mkdir myproject

cd myproject

python3 -m venv venv

## Activate the environment

. venv/bin/activate

## Requires for project sg-dashboard

pip install flask==0.10.1 flask-sqlalchemy==2.0 flask-auth==0.85 flask-api==0.6.2 pyOpenSSL==0.15.1 cryptography==0.8.2 passlib==1.6.4 sqlalchemy-migrate==0.9.6

## Try it out
 
Run the server:

$ python dashboard/run.py

Visit the dashboard: http://localhost:5001/events

