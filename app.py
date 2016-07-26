from flask import Flask
from flask import render_template
from flask_assets import Environment, Bundle
import configparser

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


@app.route('/')
def hello_world():
    return render_template('index.html', name='HATCH')

settings = configparser.ConfigParser()
settings._interpolation = configparser.ExtendedInterpolation()
settings.read('settings.ini')


@app.route('/twitter')
def twitter():
    return render_template('twitter.html')


if __name__ == '__main__':
    app.run()
