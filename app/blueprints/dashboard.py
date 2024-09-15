import flask, datetime, math
from app.helpers import *
import psutil
from config import TIME_ZONE

blueprint = flask.Blueprint("dashboard", __name__)



def get_num_with_times(cmd, *args, **kwargs):
    TIME = [datetime.datetime.now(TIME_ZONE).replace(tzinfo=None)-datetime.timedelta(weeks=1),
            datetime.datetime.now(TIME_ZONE).replace(tzinfo=None)-datetime.timedelta(days=30),
            datetime.datetime.now(TIME_ZONE).replace(tzinfo=None)-datetime.timedelta(days=183),
            datetime.datetime.now(TIME_ZONE).replace(tzinfo=None)-datetime.timedelta(days=365)]
    rtn = []
    for t in TIME:
        rtn.append(sql(cmd, str(datetime.datetime.now(TIME_ZONE).replace(tzinfo=None)), str(t), *args, *kwargs).result[0])
    return rtn

def get_num_each_hour(tname):
    TIME = [datetime.datetime.now(TIME_ZONE).replace(tzinfo=None)-datetime.timedelta(weeks=1),
            datetime.datetime.now(TIME_ZONE).replace(tzinfo=None)-datetime.timedelta(days=30),
            datetime.datetime.now(TIME_ZONE).replace(tzinfo=None)-datetime.timedelta(days=183),
            datetime.datetime.now(TIME_ZONE).replace(tzinfo=None)-datetime.timedelta(days=365)]
    rtn = []
    for t in TIME:
        arr = []
        for i in range(24):
            arr.append(sql(f"""SELECT COUNT(*) FROM {tname}_record 
                        WHERE AVAILABILITY AND APPROVED_BY IS NOT NULL AND (STIME < ? AND ETIME > ? ) AND ((TIME(STIME) < ? AND TIME(ETIME) > ?) 
                        OR (DATE(STIME) < DATE(ETIME) AND (TIME(STIME) < ? OR TIME(ETIME) > ?))
                        OR julianday(ETIME) - julianday(STIME) >= 2)""", str(datetime.datetime.now(TIME_ZONE).replace(tzinfo=None)), str(t), f"{i+1:02}:00:00", f"{i:02}:00:00", f"{i+1:02}:00:00", f"{i:02}:00:00").result[0][0])
        rtn.append(arr)

    return rtn

def get_num_each_day(tname):
    TIME = [datetime.datetime.now(TIME_ZONE).replace(tzinfo=None)-datetime.timedelta(weeks=1),
            datetime.datetime.now(TIME_ZONE).replace(tzinfo=None)-datetime.timedelta(days=30),
            datetime.datetime.now(TIME_ZONE).replace(tzinfo=None)-datetime.timedelta(days=183),
            datetime.datetime.now(TIME_ZONE).replace(tzinfo=None)-datetime.timedelta(days=365)]
    
    rtn = []
    for t in TIME:
        arr = []
        for i in weekNumToDate(dateToWeekNumber(datetime.datetime.now(TIME_ZONE).replace(tzinfo=None).date())):
            arr.append(sql(f"""SELECT COUNT(*) FROM {tname}_record 
                        WHERE AVAILABILITY AND APPROVED_BY IS NOT NULL AND (STIME < ? AND ETIME > ? ) AND (julianday(?)%7 BETWEEN julianday(STIME)%7 AND julianday(ETIME)%7) 
                        OR (julianday(ETIME)%7 < julianday(STIME)%7 AND (julianday(STIME)%7 <= julianday(?)%7 OR julianday(ETIME) >= julianday(?)%7))
                        OR (julianday(ETIME) - julianday(STIME) >= 7)""", str(datetime.datetime.now(TIME_ZONE).replace(tzinfo=None)), str(t), str(i), str(i), str(i)).result[0][0])
        rtn.append(arr)

    return rtn

def get_most_popular(tname:str):
    TIME = [datetime.datetime.now(TIME_ZONE).replace(tzinfo=None)-datetime.timedelta(weeks=1),
            datetime.datetime.now(TIME_ZONE).replace(tzinfo=None)-datetime.timedelta(days=30),
            datetime.datetime.now(TIME_ZONE).replace(tzinfo=None)-datetime.timedelta(days=183),
            datetime.datetime.now(TIME_ZONE).replace(tzinfo=None)-datetime.timedelta(days=365)]
    
    rtn1 = []
    rtn2 = []
    for t in TIME:
        result = sql(f"""SELECT a.{tname[0].upper()}ID, IFNULL(SUM(JulianDay(ETIME) - JulianDay(STIME))*24, 0) AS TD FROM {tname} a
                     LEFT JOIN {tname}_record b ON a.{tname[0].upper()}ID = b.{tname[0].upper()}ID AND b.AVAILABILITY AND APPROVED_BY IS NOT NULL AND
                     STIME < ? AND ETIME > ?
                     GROUP BY a.{tname[0].upper()}ID ORDER BY TD DESC""", str(datetime.datetime.now(TIME_ZONE).replace(tzinfo=None)), str(t)).result
        rtn1.append([result[i][1] for i in range(10)])
        rtn2.append([result[i][0] for i in range(10)])
    #print(rtn1,rtn2)
    return (rtn1,rtn2)

def bar_charts(values, categorys):
    rtn = []
    
    for i in range(len(values)):
        category = categorys[i] if type(categorys[i]) is list else categorys
        maxv = max(values[i])
        if maxv==0:
            grid_scale = 1
            maxv = 1
        else:
            grid_scale = math.floor(10**(math.floor(math.log(maxv, 10))))

            if math.log(maxv, 10)//1 > 0:

                if maxv/grid_scale <= 3:
                    grid_scale//=5
                elif maxv/grid_scale <= 8:
                    grid_scale//=2

        grid_num = math.ceil(maxv/grid_scale)+1


        scales = ''.join([f"<li style='height: {300/grid_num}px'>{i*grid_scale}</li>" for i in range(grid_num,0,-1)])
        grid_pattern =f"<div class='b2_grid_lines' style='height: {300/grid_num}px'></div>"
        bars = ''.join([f"""
                        <li style = 'width: {560/len(category)*0.9}px'>
                        <span style = 'transform: translate(-50%,{max(0, 270-values[i][j]/grid_scale/grid_num*300)}px)'>
                            {round(values[i][j],1) if type(values[i][j]) is float else values[i][j]}
                        </span>
                        <div class='bar_display' style='width: {560/len(category)*0.9}px; background-color: hsl({120*values[i][j]/maxv}, 100%, 50%);
                                transform: translateY({300-values[i][j]/grid_scale/grid_num*300}px)'>
                            </div>

                        </li>""" for j in range(len(values[i]))])
        rtn.append(f"""
        
        <table class='bar_chart'>
            <tr>
                <td class='b1'>
                    <ul>{scales}</ul>
                </td>
                <td>
                    <div class='b2'>
                        {grid_pattern * grid_num}
                        <ul class='b2_bars'>{bars}</ul>
                    </div>
                </td>
            </tr>
            <tr>
                <td class='b3'>
                    
                </td>
                <td class='b4'>
                    <ul>
                        {'<li>'+'</li><li>'.join(category)+'</li>'}
                    </ul>
                </td>
            </tr>
        </table>
        """)
    return rtn




@blueprint.route('/dashboard')
@verifySession(flask.session, role="ADMIN")
def dashboard(permission):
    ram = psutil.virtual_memory().total // 2**20
    data = {"login_times": get_num_with_times("SELECT COUNT(*) FROM login WHERE TIME < ? AND TIME > ?"),
            "room_records": get_num_with_times("SELECT COUNT(*) FROM room_record WHERE STIME < ? AND ETIME > ? "),
            "room_records_approved": get_num_with_times("SELECT COUNT(*) FROM room_record WHERE (STIME < ? AND ETIME > ? ) AND AVAILABILITY AND APPROVED_BY IS NOT NULL"),
            "facility_records": get_num_with_times("SELECT COUNT(*) FROM facility_record WHERE STIME < ? AND ETIME > ? "),
            "facility_records_approved": get_num_with_times("SELECT COUNT(*) FROM facility_record WHERE (STIME < ? AND ETIME > ? ) AND AVAILABILITY AND APPROVED_BY IS NOT NULL"),
            "room_records_num_each_hour": bar_charts(get_num_each_hour("room"), [f'{i:02}-{i+1:02}' for i in range(24)]),
            "facility_records_num_each_hour": bar_charts(get_num_each_hour("facility"), [f'{i:02}-{i+1:02}' for i in range(24)]),
            "room_records_num_each_day": bar_charts(get_num_each_day("room"), ['MON','TUE','WED','THU','FRI','SAT','SUN']),
            "facility_records_num_each_day": bar_charts(get_num_each_day("facility"), ['MON','TUE','WED','THU','FRI','SAT','SUN']),
            "most_popular_room": bar_charts(*get_most_popular("room")),
            "most_popular_facility": bar_charts(*get_most_popular("facility"))}
    #print(data["login_times"])
    return flask.render_template('dashboard.html', permission = permission, ram = ram, data=data)

@blueprint.route('/dashboard/update', methods=["POST"], endpoint = "dashboard update")
@verifySession(flask.session, role="ADMIN")
def dashboard(permission):
    return flask.jsonify({"cpu": psutil.cpu_percent(), "ram": psutil.virtual_memory().percent})