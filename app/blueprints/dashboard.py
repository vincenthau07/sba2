import flask
import datetime
from app.helpers import *
import psutil
from config import TIME_ZONE

blueprint = flask.Blueprint("dashboard", __name__)
def get_starting_time():
    return getDatetimeNow() - datetime.timedelta(days = 365)
MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', "Dec"]

def get_num_each_month():
    rtn = []
    rtn2 = []
    rtn3 = []
    m1 = getDatetimeNow().month - 11
    y1 = getDatetimeNow().year + (m1-1)//12
    m1 = (m1-1) % 12 +1
    for i in range(12):
        m2 = m1 + 1
        y2 = y1 + (m2-1)//12
        m2 = (m2-1) % 12 +1
        rtn.append(sql(f"""SELECT COUNT(*) FROM room_record WHERE STIME < ? AND ETIME >= ? 
                                AND AVAILABILITY AND APPROVED_BY IS NOT NULL""", 
                       str(datetime.datetime(year = y2, month = m2, day = 1)), 
                       str(datetime.datetime(year = y1, month = m1, day = 1))
                       ).result[0][0]
                   )
        rtn2.append(sql(f"""SELECT COUNT(*) FROM facility_record WHERE STIME < ? AND ETIME >= ? 
                                AND AVAILABILITY AND APPROVED_BY IS NOT NULL""", 
                        str(datetime.datetime(year = y2, month = m2, day = 1)), 
                        str(datetime.datetime(year = y1, month = m1, day = 1))
                        ).result[0][0]
                    )
        rtn3.append(MONTHS[m1 - 1])
        m1, y1 = m2, y2
    return [rtn, rtn2, rtn3]

def get_login_time_each_month():
    rtn = []
    rtn2 = []
    m1 = getDatetimeNow().month - 11
    y1 = getDatetimeNow().year + (m1-1)//12
    m1 = (m1-1) % 12 +1
    for i in range(12):
        m2 = m1 + 1
        y2 = y1 + (m2-1) // 12
        m2 = (m2-1) % 12 +1

        rtn.append(sql(f"""SELECT COUNT(*) FROM login WHERE TIME < ? AND TIME >= ?""", 
                       str(datetime.datetime(year = y2, month = m2, day = 1)), 
                       str(datetime.datetime(year = y1, month = m1, day = 1))).result[0][0])
        rtn2.append(MONTHS[m1-1])
        m1, y1 = m2, y2
    return [rtn, rtn2]

def get_num_each_hour(tname):
    
    rtn = []
    
    for i in range(24):
        rtn.append(sql(f"""SELECT COUNT(*) FROM {tname}_record 
                           WHERE AVAILABILITY AND APPROVED_BY IS NOT NULL AND (STIME < ? AND ETIME > ? ) AND ((TIME(STIME) < ? AND TIME(ETIME) > ?) 
                           OR (DATE(STIME) < DATE(ETIME) AND (TIME(STIME) < ? OR TIME(ETIME) > ?))
                           OR julianday(ETIME) - julianday(STIME) >= 2)""",
                       str(getDatetimeNow()),
                       str(get_starting_time()),
                       f"{i+1:02}:00:00", 
                       f"{i:02}:00:00",
                       f"{i+1:02}:00:00",
                       f"{i:02}:00:00"
                   ).result[0][0]
        )
    return rtn

def get_num_each_day(tname):
    
    rtn = []
    for i in weekNumToDate(dateToWeekNumber(getDatetimeNow().date())):
        rtn.append(sql(f"""SELECT COUNT(*) FROM {tname}_record 
                       WHERE AVAILABILITY AND 
                                APPROVED_BY IS NOT NULL AND 
                                (STIME < ? AND ETIME > ? ) AND 
                                (julianday(?)%7 BETWEEN julianday(STIME)%7 AND julianday(ETIME)%7) OR
                            (julianday(ETIME)%7 < julianday(STIME)%7 AND 
                                (julianday(STIME)%7 <= julianday(?)%7 OR julianday(ETIME) >= julianday(?)%7)) OR
                            (julianday(ETIME) - julianday(STIME) >= 7)""", 
                       str(getDatetimeNow()), 
                       str(get_starting_time()), 
                       str(i), 
                       str(i), 
                       str(i)
                   ).result[0][0]
        )

    return rtn

def get_most_popular(tname:str):
    
    result = sql(f"""SELECT a.{tname[0].upper()}ID, IFNULL(SUM(JulianDay(ETIME) - JulianDay(STIME))*24, 0) AS TD FROM {tname} a
                 LEFT JOIN {tname}_record b ON a.{tname[0].upper()}ID = b.{tname[0].upper()}ID AND 
                 b.AVAILABILITY AND 
                 APPROVED_BY IS NOT NULL AND
                 STIME < ? AND 
                 ETIME > ?
                 GROUP BY a.{tname[0].upper()}ID ORDER BY TD DESC""", 
                 str(getDatetimeNow()), 
                 str(get_starting_time())).result

    return [[result[i][1] for i in range(10)], 
            [result[i][0] for i in range(10)]]



@blueprint.route('/dashboard')
@verifySession(flask.session, role = "ADMIN")
def dashboard(permission):
    ram = psutil.virtual_memory().total // 2**20
    r_hour = get_num_each_hour('room')
    f_hour = get_num_each_hour('facility')
    data = {
        'login': get_login_time_each_month(),
        'month_r_f': get_num_each_month(),
        'hour_r_f_am': [r_hour[:12], f_hour[:12]],
        'hour_r_f_pm': [r_hour[12:], f_hour[12:]],
        'weekday_r_f': [get_num_each_day('room'), get_num_each_day('facility')],
        '10_r': get_most_popular('room'),
        '10_f': get_most_popular('facility')
    }
    return flask.render_template('dashboard.html', 
                                 permission = permission, 
                                 ram = ram, 
                                 data = data, 
                                 tz = TIME_ZONE)

@blueprint.route('/dashboard/update', methods = ["GET"])
@verifySession(flask.session, role = "ADMIN")
def dashboardPOST(permission):
    return flask.jsonify({"cpu": psutil.cpu_percent(interval = 1, percpu = False), "ram": psutil.virtual_memory().percent})
