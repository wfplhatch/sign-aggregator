# HATCH Makerspace Sign Aggregator
> "It puts calendar stuff on a screen."

## Development Setup

1. Create a virtualenv, source it.
2. `pip install -r requirements.txt`
3. Get a [Google API service account](https://developers.google.com/identity/protocols/OAuth2ServiceAccount), 
download the keyfile, and name it `keyfile.json` in this dir

## Running in development
Run the app using the built-in Flask web server

1. Source the right virtualenv
2. `python app.py`

## Running in "production"
Using the Flask web server is good for dev, but for "production" we'll use uwsgi.


1. Source the virtualenv
2. `uwsgi uwsgi.ini`