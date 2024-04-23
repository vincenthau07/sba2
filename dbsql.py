import sqlite3
conn = sqlite3.connect("database/user.sqlite", check_same_thread=False)
cur = conn.cursor()

def sql(cmd,*params):
    cur.execute(cmd, params)
    return cur.fetchall()
def modify(cmd, *params):
    print(cmd)
    cur.execute(cmd, params)
    
    conn.commit()
    return cur.fetchall()
def getSchedule(rid,stime,etime):
    return sql("""SELECT STIME, ETIME, PURPOSE 
               FROM bookingrecord 
               WHERE RID = ? AND 
               (? BETWEEN STIME AND ETIME OR
                ? BETWEEN STIME AND ETIME OR
                STIME BETWEEN ? AND ?)""",rid,stime,etime,stime,etime)
def getUsername(uid):
    return sql(f"SELECT UNAME FROM user WHERE UID = ?", uid)[0][0]
    
def getPassword(uid):
    rtn = sql(f"SELECT PASSWORD FROM user WHERE UID = ?", uid)
    
    if len(rtn):
        return rtn[0][0]
    else:
        return None
    
def getRoomName(rid):
    return sql(f"SELECT RNAME FROM room WHERE RID = '{rid}' ORDER BY RID ASC")[0][0]

def getPermission(uid):
    rtn = {}
    perm = list(sql("""SELECT * FROM roles 
               WHERE ROLE = (SELECT ROLE FROM user WHERE UID = ?)
    """, uid)[0])
    i = 0
    for field in cur.description:
        if field[0] != "UID":
            rtn[field[0]] = perm[i]
        i += 1
    return rtn
