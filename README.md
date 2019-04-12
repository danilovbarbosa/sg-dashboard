# sg-dashboard
A dashboard to visualize game data.

## Requires for Dev

```
$ sudo apt-get install build-essential libssl-dev libffi-dev python3-dev 

$ sudo apt-get install git python-pip make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev curl
```

## Create an environment (Linux)

```
$ mkdir myproject

$ cd myproject

$ python3 -m venv venv
```

## Activate the environment

``` $ . venv/bin/activate ```

## Requires for project sg-dashboard

``` $ pip install -r requirements.txt ``` 

## Try it out

###  Clone project (branch sg-l2ForDeaf):

``` $ git clone -b sg-l2ForDeaf https://github.com/danilovbarbosa/sg-dashboard.git ``` 
 
### Run the server:

``` $  python dashboard/run.py ``` 

> Visit the dashboard: http://localhost:5001/events

