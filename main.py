import flask, os
import datetime
from server import *
import modules.sql as sql
# html initialise
app = flask.Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(hours=2)

import webpages.booking
import webpages.home
import webpages.login
import webpages.logout
import webpages.records
import webpages.sql
import webpages.users

if __name__ == '__main__':
    app.debug=False
    app.run(host=IP,port=PORT)