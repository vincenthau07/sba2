import flask, datetime, math, copy
from app.helpers import *
import psutil
from config import TIME_ZONE

blueprint = flask.Blueprint("dashboard", __name__)
def TIME():
    return datetime.datetime.now(TIME_ZONE).replace(tzinfo=None)-datetime.timedelta(days=365)
MONTH = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov',"Dec"]

def get_num_each_month():
    rtn = []
    rtn2 = []
    rtn3 = []
    m1 = datetime.datetime.now(TIME_ZONE).replace(tzinfo=None).month - 11
    y1 = datetime.datetime.now(TIME_ZONE).replace(tzinfo=None).year + (m1-1)//12
    m1 = (m1-1)%12+1
    for i in range(12):
        m2 = m1 + 1
        y2 = y1 + (m2-1)//12
        m2 = (m2-1) % 12 +1
        rtn.append(sql(f"""SELECT COUNT(*) FROM room_record WHERE STIME < ? AND ETIME >= ?""", str(datetime.datetime(year=y2, month=m2, day=1)), str(datetime.datetime(year=y1, month=m1, day=1))).result[0][0])
        rtn2.append(sql(f"""SELECT COUNT(*) FROM facility_record WHERE STIME < ? AND ETIME >= ?""", str(datetime.datetime(year=y2, month=m2, day=1)), str(datetime.datetime(year=y1, month=m1, day=1))).result[0][0])
        rtn3.append(MONTH[m1-1])
        m1, y1 = m2, y2
    return [rtn, rtn2, rtn3]

def get_login_time_each_month():
    rtn = []
    rtn2 = []
    m1 = datetime.datetime.now(TIME_ZONE).replace(tzinfo=None).month - 11
    y1 = datetime.datetime.now(TIME_ZONE).replace(tzinfo=None).year + (m1-1)//12
    m1 = (m1-1) % 12 +1
    for i in range(12):
        m2 = m1 + 1
        y2 = y1 + (m2-1)//12
        m2 = (m2-1) % 12 +1

        rtn.append(sql(f"""SELECT COUNT(*) FROM login WHERE TIME < ? AND TIME >= ?""", str(datetime.datetime(year=y2, month=m2, day=1)), str(datetime.datetime(year=y1, month=m1, day=1))).result[0][0])
        rtn2.append(MONTH[m1-1])
        m1, y1 = m2, y2
    return [rtn, rtn2]

def get_num_each_hour(tname):
    
    rtn = []
    
    for i in range(24):
        rtn.append(sql(f"""SELECT COUNT(*) FROM {tname}_record 
                    WHERE AVAILABILITY AND APPROVED_BY IS NOT NULL AND (STIME < ? AND ETIME > ? ) AND ((TIME(STIME) < ? AND TIME(ETIME) > ?) 
                    OR (DATE(STIME) < DATE(ETIME) AND (TIME(STIME) < ? OR TIME(ETIME) > ?))
                    OR julianday(ETIME) - julianday(STIME) >= 2)""", str(datetime.datetime.now(TIME_ZONE).replace(tzinfo=None)), str(TIME()), f"{i+1:02}:00:00", f"{i:02}:00:00", f"{i+1:02}:00:00", f"{i:02}:00:00").result[0][0])
    return rtn

def get_num_each_day(tname):
    
    rtn = []
    for i in weekNumToDate(dateToWeekNumber(datetime.datetime.now(TIME_ZONE).replace(tzinfo=None).date())):
        rtn.append(sql(f"""SELECT COUNT(*) FROM {tname}_record 
                    WHERE AVAILABILITY AND APPROVED_BY IS NOT NULL AND (STIME < ? AND ETIME > ? ) AND (julianday(?)%7 BETWEEN julianday(STIME)%7 AND julianday(ETIME)%7) 
                    OR (julianday(ETIME)%7 < julianday(STIME)%7 AND (julianday(STIME)%7 <= julianday(?)%7 OR julianday(ETIME) >= julianday(?)%7))
                    OR (julianday(ETIME) - julianday(STIME) >= 7)""", str(datetime.datetime.now(TIME_ZONE).replace(tzinfo=None)), str(TIME()), str(i), str(i), str(i)).result[0][0])

    return rtn

def get_most_popular(tname:str):
    
    result = sql(f"""SELECT a.{tname[0].upper()}ID, IFNULL(SUM(JulianDay(ETIME) - JulianDay(STIME))*24, 0) AS TD FROM {tname} a
                 LEFT JOIN {tname}_record b ON a.{tname[0].upper()}ID = b.{tname[0].upper()}ID AND b.AVAILABILITY AND APPROVED_BY IS NOT NULL AND
                 STIME < ? AND ETIME > ?
                 GROUP BY a.{tname[0].upper()}ID ORDER BY TD DESC""", str(datetime.datetime.now(TIME_ZONE).replace(tzinfo=None)), str(TIME())).result

    return [[result[i][1] for i in range(10)], [result[i][0] for i in range(10)]]



@blueprint.route('/dashboard')
@verifySession(flask.session, role="ADMIN")
def dashboard(permission):
    ram = psutil.virtual_memory().total // 2**20
    # data = {"login_times": get_num_with_times("SELECT COUNT(*) FROM login WHERE TIME < ? AND TIME > ?"),
    #         "room_records": get_num_with_times("SELECT COUNT(*) FROM room_record WHERE STIME < ? AND ETIME > ? "),
    #         "room_records_approved": get_num_with_times("SELECT COUNT(*) FROM room_record WHERE (STIME < ? AND ETIME > ? ) AND AVAILABILITY AND APPROVED_BY IS NOT NULL"),
    #         "facility_records": get_num_with_times("SELECT COUNT(*) FROM facility_record WHERE STIME < ? AND ETIME > ? "),
    #         "facility_records_approved": get_num_with_times("SELECT COUNT(*) FROM facility_record WHERE (STIME < ? AND ETIME > ? ) AND AVAILABILITY AND APPROVED_BY IS NOT NULL"),
    #         "room_records_num_each_hour": bar_charts(get_num_each_hour("room"), [f'{i:02}-{i+1:02}' for i in range(24)]),
    #         "facility_records_num_each_hour": bar_charts(get_num_each_hour("facility"), [f'{i:02}-{i+1:02}' for i in range(24)]),
    #         "room_records_num_each_day": bar_charts(get_num_each_day("room"), ['MON','TUE','WED','THU','FRI','SAT','SUN']),
    #         "facility_records_num_each_day": bar_charts(get_num_each_day("facility"), ['MON','TUE','WED','THU','FRI','SAT','SUN']),
    #         "most_popular_room": bar_charts(*get_most_popular("room")),
    #         "most_popular_facility": bar_charts(*get_most_popular("facility"))}\
    #print(data["login_times"])
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
    return flask.render_template('dashboard.html', permission = permission, ram = ram, data=data)

@blueprint.route('/dashboard/update', methods=["POST"], endpoint = "dashboard update")
@verifySession(flask.session, role="ADMIN")
def dashboard(permission):
    return flask.jsonify({"cpu": psutil.cpu_percent(), "ram": psutil.virtual_memory().percent})
