import flask, datetime
import modules.sql as sql
import modules.html as html

management_bp = flask.Blueprint("room management", __name__)

PK = {"room": "RID",
      "user": "UID",
      "roles": "ROLE",
      "facilityrecord": "BID",
      "roomrecord": "BID",
      "facility": "FID",
      "schoolunit": "UNIT"}

def input_format(tname: str):
    match tname:
        case "room":
            return {
                "FLOOR": ["number"],
                "AREA": ["number"],
                "CAPACITY": ["number"],
                "AVAILABILITY": ["checkbox"]
            }
        case "user":
            return {
                "ROLE": ["select", [row[0] for row in sql.sql("SELECT ROLE FROM ROLES ORDER BY ROLE").result]],
                "SEX": ["select", ["M", "F"]]
            }
        case "roles": 
            return {
                "EDITUSER": ["checkbox"],
                "EDITROOM": ["checkbox"],
                "ADDRECORD": ["checkbox"],
                "EDITROOMRECORD": ["checkbox"],
                "EDITFACILITY": ["checkbox"],
                "EDITSCHOOLUNIT": ["checkbox"],
                "EDITFACILITYRECORD": ["checkbox"],
                "EDITROLES": ["checkbox"]
            }
        case "facilityrecord":
            return {
                "BID": ["number"],
                "STIME": ["datetime"],
                "ETIME": ["datetime"],
                "UID": ["select", [row[0] for row in sql.sql("SELECT UID FROM user ORDER BY UID").result]],
                "FID": ["select", [row[0] for row in sql.sql("SELECT FID FROM facility ORDER BY FID").result]],
                "UNIT": ["select", [row[0] for row in sql.sql("SELECT UNIT FROM schoolunit ORDER BY UNIT").result]],
                "APPROVED_BY": ["select", [row[0] for row in sql.sql("SELECT UID FROM user u, roles r WHERE u.ROLE = r.ROLE AND EDITFACILITYRECORD ORDER BY UID").result]+[None]],
                "AVAILABILITY": ["checkbox"]
            }
        case "roomrecord":
            return {
                "BID": ["number"],
                "STIME": ["datetime"],
                "ETIME": ["datetime"],
                "UID": ["select", [row[0] for row in sql.sql("SELECT UID FROM user ORDER BY UID").result]],
                "RID": ["select", [row[0] for row in sql.sql("SELECT RID FROM room ORDER BY RID").result]],
                "UNIT": ["select", [row[0] for row in sql.sql("SELECT UNIT FROM schoolunit ORDER BY UNIT").result]],
                "APPROVED_BY": ["select", [row[0] for row in sql.sql("SELECT UID FROM user u, roles r WHERE u.ROLE = r.ROLE AND EDITROOMRECORD ORDER BY UID").result]+[None]],
                "AVAILABILITY": ["checkbox"]
            }
        case "facility": 
            return {
                "AVAILABILITY": ["checkbox"]
            }
        case "schoolunit": 
            return {
                "UNIT": ["number"]
            }


def info(tname, tableOnly = False):
    info = sql.sql(f"SELECT * FROM {tname} ORDER BY {PK[tname]}",tupleToList=True)

    for i in info.result:
        i.append(html.input({"name": i[0], "type": "submit", "value": "Edit"}))
        i.append(html.input({"name": i[0], "type": "submit", "value": "Delete"}))
    #info.field_display.append("#Edit")
    info.field_display.append("")
    info.field_display.append("")
    
    table = html.table(info.field_display, info.result, {"class": "sortable"})
    table += html.input({"name": "add", "type": "submit", "value": "+"})

    if not tableOnly:
        return table, info.field, input_format(tname)
    else:
        return table


@management_bp.route('/management/<tname>', methods=["GET"])
def management(tname):
    if not sql.commands.sessionValidity(flask.session):
        return flask.redirect('/login')
    permission = sql.commands.rolePermissions(flask.session.get('UID'))
    if tname not in PK or not permission["EDIT"+ tname.upper()]:
        return flask.redirect('/home')
    
    table, field, input_format = info(tname)
    
    return flask.render_template('management.html', permission=permission, tname=tname, table=table, field=field, input_format=input_format)


@management_bp.route('/management/<tname>/<action>', methods=["POST"])
def managementPOST(tname, action):
    if not sql.commands.sessionValidity(flask.session):
        return flask.redirect('/login')
    permission = sql.commands.rolePermissions(flask.session.get('UID'))
    if tname not in PK or not permission["EDIT"+ tname.upper()]:
        return flask.redirect('/home')
    
    try:
        if action in ("update", "delete"):
            sql.sql(f"DELETE FROM {tname} WHERE {PK[tname]} = ?", flask.request.form.get("id"), commit=True)

        if action in ("update", "insert"):
            length = len(flask.request.form.getlist("data[]"))
            placeholders = ','.join(['?'] * length)
            sql.sql(f"INSERT INTO {tname} VALUES ({placeholders})", *flask.request.form.getlist("data[]"), commit=True)
    except Exception as e:
        return flask.jsonify({"error": e})

    table = info(tname, tableOnly=True)
    
    if action == "reload":
        return flask.jsonify(table=table)
    else:
        return flask.jsonify({"table": table, "error": "Succeed."})