import flask, datetime
from app.helpers import *
import psutil

blueprint = flask.Blueprint("dashboard", __name__)

def get_num_with_times(cmd, *args, paranum=1,**kwargs):
    TIME = [datetime.datetime.now()-datetime.timedelta(weeks=1),
            datetime.datetime.now()-datetime.timedelta(days=30),
            datetime.datetime.now()-datetime.timedelta(days=183),
            datetime.datetime.now()-datetime.timedelta(days=365)]
    rtn = []
    for i in range(len(TIME)):
        rtn.append(sql(cmd, *[str(datetime.datetime.now()) if j%2 else str(TIME[i]) for j in range(paranum*2)], *args, *kwargs).result[0])
    return rtn

@blueprint.route('/dashboard')
@verifySession(flask.session, role="ADMIN")
def dashboard(permission):
    ram = psutil.virtual_memory().total // 2**20
    data = {"login_times": get_num_with_times("SELECT COUNT(*) FROM login WHERE TIME BETWEEN ? AND ?"),
            "room_records": get_num_with_times("SELECT COUNT(*) FROM room_record WHERE STIME BETWEEN ? AND ? OR ETIME BETWEEN ? AND ?", paranum=2),
            "room_records_approved": get_num_with_times("SELECT COUNT(*) FROM room_record WHERE (STIME BETWEEN ? AND ? OR ETIME BETWEEN ? AND ?) AND AVAILABILITY AND APPROVED_BY IS NOT NULL", paranum=2),
            "facility_records": get_num_with_times("SELECT COUNT(*) FROM facility_record WHERE STIME BETWEEN ? AND ? OR ETIME BETWEEN ? AND ?", paranum=2),
            "facility_records_approved": get_num_with_times("SELECT COUNT(*) FROM facility_record WHERE (STIME BETWEEN ? AND ? OR ETIME BETWEEN ? AND ?) AND AVAILABILITY AND APPROVED_BY IS NOT NULL", paranum=2),
            }

    print(ram, psutil.virtual_memory().total)
    return flask.render_template('dashboard.html', permission = permission, ram = ram, data=data)

@blueprint.route('/dashboard/update', methods=["POST"], endpoint = "dashboard update")
@verifySession(flask.session, role="ADMIN")
def dashboard(permission):
    return flask.jsonify({"cpu": psutil.cpu_percent(), "ram": psutil.virtual_memory().percent})