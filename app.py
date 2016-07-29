from __future__ import print_function
from flask import Flask
from flask import render_template
from flask_assets import Environment, Bundle

import httplib2
import os
import datetime

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools
from oauth2client import file

app = Flask(__name__)

assets = Environment(app)

js = Bundle(
    'bower_components/bootflat/js/bootstrap.js',
    'bower_components/bootflat/js/html5shiv.js',
    'bower_components/bootflat/js/jquery-1.10.1.min.js',
    'bower_components/bootflat/js/jquery.icheck.js',
    'bower_components/bootflat/js/respond.min.js',
    filters='jsmin',
    output='js_all.js'
)
assets.register('js_all', js)

css = Bundle(
    'bower_components/bootflat/bootstrap/bootstrap.css',
    'bower_components/bootflat/css/bootflat.css',
    'bower_components/bootflat/css/bootflat-extensions.css',
    'bower_components/bootflat/css/font-awesome.min.css',
    output='css_all.css'
)
assets.register('css_all', css)

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Calendar API Python Quickstart'
CALENDAR_NAME = 'wfplmakerspace@gmail.com'

def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'calendar-python-quickstart.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

credentials = get_credentials()
http = credentials.authorize(httplib2.Http())
service = discovery.build('calendar', 'v3', http=http)

@app.template_filter('strftime')
def datetimeformat(value, format='%H:%M / %d-%m-%Y'):
        for fmt in ('%Y-%M-%d', '%Y-%m-%dT%H:%M:%SZ'):
            try:
                dang = datetime.datetime.strptime(value, fmt)
                return dang.strftime(format)
            except ValueError:
                pass
        raise ValueError('no valid date format found')

@app.route('/')
def upcoming_hours():
    now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    print('Getting the upcoming 10 events')
    eventsResult = service.events().list(
        calendarId=CALENDAR_NAME, timeMin=now, maxResults=10, singleEvents=True,
        orderBy='startTime').execute()
    events = eventsResult.get('items', [])

    if not events:
        print('No upcoming events found.')
    hours = filter(lambda event: ('Open' in event['summary'] and len(event['summary'])< 10) or ('Closed' in event['summary']), events)

    return render_template('index.html', name='HATCH', events=hours)

@app.route('/rawfeed')
def raw_feed():
    now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    print('Getting the upcoming 10 events')
    eventsResult = service.events().list(
        calendarId=CALENDAR_NAME, timeMin=now, maxResults=10, singleEvents=True,
        orderBy='startTime').execute()
    events = eventsResult.get('items', [])

    if not events:
        print('No upcoming events found.')
    return render_template('rawfeed.html', events=events)

if __name__ == '__main__':
    app.run()
