import pyodbc
DRIVER="{Microsoft Access Driver (*.mdb, *.accdb)}"
conn = pyodbc.connect('DRIVER={};DBQ={}'.format(DRIVER,"database/user.accdb"))
cur = conn.cursor()

def sql(cmd,*params):
    cur.execute(cmd, *params)
    return cur.fetchall()
def modify(cmd,*params):
    cur.execute(cmd,*params)
    cur.commit()
def getSchedule(rid,stime,etime):
    return sql("""SELECT STIME, ETIME, PURPOSE 
               FROM bookingrecord 
               WHERE RID = ? AND 
               (? BETWEEN STIME AND ETIME OR
                ? BETWEEN STIME AND ETIME OR
                STIME BETWEEN ? AND ?)""",rid,stime,etime,stime,etime)
def getUsername(uid):
    return sql(f"SELECT UNAME FROM user WHERE UID = '{uid}'")[0][0]
    
def getPassword(uid):
    rtn = sql(f"SELECT PASSWORD FROM user WHERE UID = '{uid}'")
    if len(rtn):
        return rtn[0][0]
    else:
        return None
    
def getRoomName(rid):
    return sql(f"SELECT RNAME FROM room WHERE RID = '{rid}' ORDER BY RID ASC")[0][0]
