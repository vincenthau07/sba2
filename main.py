import flask, os
import datetime
import time
from server import *

#initial flask
app = flask.Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(hours=2)
#load all webpages from path "/routes"
from routes.booking import booking_bp
app.register_blueprint(booking_bp)
from routes.home import home_bp
app.register_blueprint(home_bp)
from routes.login import login_bp
app.register_blueprint(login_bp)
from routes.logout import logout_bp
app.register_blueprint(logout_bp)
from routes.myRecords import myRecords_bp
app.register_blueprint(myRecords_bp)
from routes.sqlWeb import sql_bp
app.register_blueprint(sql_bp)

from routes.management import management_bp
app.register_blueprint(management_bp)
# from routes.userManagement import userManagement_bp
# app.register_blueprint(userManagement_bp)
# from routes.recordManagement import recordManagement_bp
# app.register_blueprint(recordManagement_bp)
# from routes.roomManagement import roomManagement_bp
# app.register_blueprint(roomManagement_bp)

#start website
if __name__ == '__main__':
    app.debug=True
    app.run(host=IP,port=PORT)