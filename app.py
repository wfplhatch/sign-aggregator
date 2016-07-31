from __future__ import print_function

import atexit
import datetime
import os.path
import json
import dateutil.parser
from apiclient import discovery
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from flask import Flask, render_template
from flask_assets import Environment, Bundle
from httplib2 import Http
from oauth2client import tools
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)

print("Welcome to the sign-aggregator!")

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

# application constants
API_SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
CLIENT_SECRET_FILE = 'keyfile.json'
APPLICATION_NAME = 'sign-aggregator'
CALENDAR_NAME = 'wfplmakerspace@gmail.com'
POLLING_INTERVAL = 120
MAX_RESULTS = 10


# get service account credentials on the specified API_SCOPES
def get_credentials():
    if os.path.isfile(CLIENT_SECRET_FILE):
        credentials = ServiceAccountCredentials.from_json_keyfile_name(CLIENT_SECRET_FILE, scopes=API_SCOPES)
    else:
        keyfile_data=json.loads(os.environ.get('KEYFILE'))
        credentials = ServiceAccountCredentials.from_json_keyfile_dict(keyfile_dict=keyfile_data,scopes=API_SCOPES)
    return credentials


credentials = get_credentials()

# Authenticate and provision the calendar service
print("Authenticating...")
http_auth = credentials.authorize(Http())
print("Provisioning API services... ")
service = discovery.build('calendar', 'v3', http=http_auth)


def get_events():
    now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    print('Getting the upcoming 10 events')
    eventsResult = service.events().list(
        calendarId=CALENDAR_NAME, timeMin=now, maxResults=MAX_RESULTS, singleEvents=True,
        orderBy='startTime').execute()
    global events
    events = eventsResult.get('items', [])

    if not events:
        print('No upcoming events found.')
    global hours
    hours = filter(
        lambda event: ('Open' in event['summary'] and len(event['summary']) < 10) or ('Closed' in event['summary']),
        events)


# Get the events once before the routes are brought online
get_events()

# Set up a scheduler to get events on an interval
print("Provisioning background job scheduler...")
scheduler = BackgroundScheduler()
scheduler.start()
scheduler.add_job(
    func=get_events,
    trigger=IntervalTrigger(seconds=POLLING_INTERVAL),
    id='event_polling_job',
    name='Get event data every minute',
    replace_existing=True)
atexit.register(lambda: scheduler.shutdown())


# this filter gives you weekday and time with AM/PM
@app.template_filter('weekdaytime')
def datetimeformat(value, format='%A %b %d, %I:%M %p'):
    dang = dateutil.parser.parse(value)
    return dang.strftime(format)


# this filter gives you just the time with AM/PM
@app.template_filter('justtime')
def datetimeformat(value, format='%I:%M %p'):
    dang = dateutil.parser.parse(value)
    return dang.strftime(format)


# Simple "welcome" page
@app.route('/')
def home_page():
    return render_template('index.html')


# Google Calendar Hours page
@app.route('/hours')
def upcoming_hours():
    return render_template('hours.html', name='HATCH', events=hours)


# raw event query feed for debugging / development
@app.route('/rawfeed')
def raw_feed():
    return render_template('rawfeed.html', events=events)


# in the event of a 404...
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run()
