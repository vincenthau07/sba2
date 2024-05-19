import sqlite3, datetime
conn = sqlite3.connect("database/database.sqlite", check_same_thread=False)
cur = conn.cursor()
FIELD_NAME = {
    "STIME": "Starting Datetime",
    "ETIME": "Ending Datetime",
    "PENDING": "Pending",
    "AVAILABILITY": "Availability",
    "ROLE": "Role",
    "RNAME": "Room Name",
    "FLOOR": "Floor",
    "CAPACITY": "Capacity",
    "PASSWORD": "Password",
    "SEX": "Sex",
    "EMAIL": "Email",
    "UNAME": "Name",
    "PURPOSE": "Purpose"
}

class sql():
    def __init__(self,cmd,*params,commit=None, tupleToList=False) -> None:
        cur.execute(cmd, params)
        if commit:
            conn.commit()
        self.result = cur.fetchall()
        if cur.description:
            self.field = [i[0] for i in cur.description]
            self.field_display = []
            for i in self.field:
                if i in FIELD_NAME:
                    self.field_display.append(FIELD_NAME[i])
                else:
                    self.field_display.append(i)
        else:
            self.field = None
        if tupleToList:
            self.result = [list(arr) for arr in self.result]

class commands():
    def userPassword(uid,*params) -> str:
        return sql(f"SELECT PASSWORD FROM user WHERE UID = ?", uid,*params).result[0][0]

    def userName(uid,*params) -> str:
        return sql(f"SELECT UNAME FROM user WHERE UID = ?", uid,*params).result[0][0]
    
    def sessionValidity(session):
        if 'UID' not in session or 'password' not in session:
            return False
        try:
            pw = commands.userPassword(session["UID"])
        except TypeError:
            return False
        if pw==session["password"]:
            return True
        return False

    def roomName(rid,*params) -> str:
        return sql(f"SELECT RNAME FROM room WHERE RID = '{rid}'",*params).result[0][0]
    
    def recordInfo(rid,stime,etime,*params) -> list:
        return sql("""SELECT STIME, ETIME, PURPOSE, PENDING
                       FROM bookingrecord 
                       WHERE RID = ? AND 
                       (? BETWEEN STIME AND ETIME OR
                        ? BETWEEN STIME AND ETIME OR
                        STIME BETWEEN ? AND ? AND
                        (AVAILABILITY OR PENDING))""",rid,stime,etime,stime,etime, tupleToList=True,*params)
    
    def rolePermissions(uid=None,role=None):
        if uid:
            result = sql("""SELECT * FROM roles 
                            WHERE ROLE = (SELECT ROLE FROM user WHERE UID = ?)
                            """, uid)
            
        if role:
            result = sql("""SELECT * FROM roles 
                            WHERE ROLE = ?
                            """, role)
        permissions = {}
        for i in range(len(result.field)):
            permissions[result.field[i]] = result.result[0][i]
        return permissions