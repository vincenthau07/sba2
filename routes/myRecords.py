import flask, datetime
import modules.sql as sql
import modules.html as html

myRecords_bp = flask.Blueprint("myRecords", __name__)

@myRecords_bp.route('/my-records', methods=["GET", "POST"])

def records():
    if not sql.commands.sessionValidity(flask.session):
        return flask.redirect('/login')
    permission = sql.commands.rolePermissions(flask.session.get('UID'))
    if not permission["ADDRECORD"]:
        return flask.redirect('/home')
    remark = ''
    table = ''
    if flask.request.method == 'POST':
        for i in flask.request.form:
            try:
                sql.sql(f"UPDATE bookingrecord SET AVAILABILITY = 0, PENDING = 0 WHERE UID = '{flask.session.get('UID')}' AND BID = {i}",commit=True)
                remark = "Cancellation succeed."
            except Exception as e:
                remark = e
    
    result = sql.sql(f"SELECT BID, STIME, ETIME, a.RID, RNAME, PURPOSE FROM bookingrecord a, room b WHERE UID = \'{flask.session.get('UID')}\' AND a.RID = b.RID AND ETIME>=?", str(datetime.datetime.today()),tupleToList=True)
    if result.result:
        for i in result.result:
            i.append('''<input class = "button" type="submit" name="{{ i[0] }}" value="Cancel">''')
        table = html.table(result.field_display+["#Cancel"], result.result, {"class": "sortable"})
    return flask.render_template('records.html', remark=remark, table=table, permission = permission)