import datetime

def dateToWeekNum(date: datetime.datetime):
    date += datetime.timedelta(days=4-datetime.date.isoweekday(date))
    date2 = datetime.date(date.year,1,1)
    date2 += datetime.timedelta(days=(11-datetime.date.isoweekday(date2))%7-3)
    return f"{date.year}-W{(date-date2).days//7+1:02d}"

def weekNumToDate(week):
    year = int(week[:4])
    week = int(week[-2:])
    date = datetime.date(year,1,1)
    date += datetime.timedelta(days=(11-datetime.date.isoweekday(date))%7-3)
    date += datetime.timedelta(days=(week-1)*7)
    d = datetime.timedelta(days=1)
    rtn = []
    for i in range(7):
        rtn.append(date)
        date += d
    return rtn

def strToDate(string):
    return datetime.datetime(int(string[:4]),int(string[5:7]),int(string[8:10]),int(string[11:13]),int(string[14:16]))