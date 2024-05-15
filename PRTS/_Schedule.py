"""
    PRTS Schedu Module
    To ensure the performance of the schedule, the schedule is traversed every 30 seconds to check all conditions.
"""
from threading import *
from copy import *
import time
import re
class PRTSSchedule:
    """
    # PRTS Schedule
    To use the class, you need to inherit it and implement the `todo` method.\n
    And you have to call the `setTime`, `setDay`, `setMonth` method to set the schedule.
    # Warning
    The `todo` method will be executed in `PRTS Schedule Thread`, not in the `main thread`.\n
    You have to ensure that the `todo` method is thread-safe.\n
    If you are using PySide or similar frameworks with event loops, 
    we generally recommend using event systems with these frameworks. 
    That is, an event is triggered from the `todo` function, 
    and then processed by another function in the main thread.\n
    In this case, this schedule is just an advanced timing trigger facility, 
    rather than the main carrier of logical code.\n
    This is relatively safe, otherwise you may need to deal with some mutex and other facilities, 
    and it is highly likely to make a mess of the program, and then crash the program in case of mutex conflicts
    """
    def __init__(this):
        pass
    def setTime(this, time:str):
        """
        Must be in the format of "HH:MM" (24-hour , and must be four digits, eg, 05:30)

        Can use `?`to represents any value, 
        this schedu will be executed every time a match is met.

        eg, `??:20` means every hour at 20 minutes
        """
        this._time = time

    def setDay(this, day:str):
        """
        No matter how much data you enter, please use commas to separate them. 
        Spaces are allowed before and after commas.
        Notice : All date identifiers are related to `OR`, not to `AND`
        # Week-input
        Sunday, Monday, Tuesday, Wednesday, Thursday, Friday, Saturday
        # Day-input
        01, ..., 31. (must be two digits, eg, 05)\n
        Day-input allows the use of `?` to represent any value.

        """
        this._day = day

    def setMonth(this, month:str):
        """
        No matter how much data you enter, please use commas to separate them. 
        Spaces are allowed before and after commas.
        Notice : All date identifiers are related to `OR`, not to `AND`
        # Month-input
        January, February, March, April, May, June, July, August, September, October, November, December
        # Month-input
        01, ..., 12. (must be two digits, eg, 05)\n
        Month-input allows the use of `?` to represent any value.
        """
        this._month = month

    def todo():
        pass

class PRTSScheduleManager(Thread):
    mutex = Lock()
    def __init__(this):
        super().__init__()
        this.scheduList = []
        this.start()

    def addSchedule(this, schedu:PRTSSchedule):
        this.mutex.acquire()
        this.scheduList.append(schedu)
        this.mutex.release()

    def run(this):
        sleepDelta = 0
        while True:
            startTime = time.time()
            this.mutex.acquire()
            scheduList = copy(this.scheduList) # do not deep copy
            this.mutex.release()
            length = len(scheduList)
            if length != 0:
                everyScheduleTime = 60.0 / length
                for schedu in scheduList:
                    schedustartTime = time.time()
                    this.checkSchedu(schedu)
                    scheduendTime = time.time()
                    rawSleepTime = everyScheduleTime - (scheduendTime - schedustartTime)
                    if scheduendTime - schedustartTime < everyScheduleTime:
                        time.sleep(everyScheduleTime - (scheduendTime - schedustartTime))
                        sleepTime = time.time() - scheduendTime
                        sleepDelta = sleepTime - rawSleepTime
            endTime = time.time()
            rawSleepTime = 60 - (endTime - startTime)
            if endTime - startTime < 60:
                time.sleep(60 - (endTime - startTime) - sleepDelta)
                sleepTime = time.time() - endTime
                sleepDelta = sleepTime - rawSleepTime

    def checkSchedu(this, schedu:PRTSSchedule):
        nowday_w = time.strftime("%A", time.localtime())
        nowmonth = time.strftime("%m", time.localtime())
        nowday_m = time.strftime("%d", time.localtime())
        now_H = time.strftime("%H", time.localtime())
        now_M = time.strftime("%M", time.localtime())
        sameday = False
        if schedu._day != None:
            scheduday = schedu._day.split(",")
            scheduday = [i.strip() for i in scheduday]
            if nowday_w in scheduday:
                sameday = True
            for day in scheduday:
                day = day.replace("?", "[0-9]")
                if re.match("^"+day+"$", nowday_m) != None:
                    sameday = True
                    break
        if not sameday: return
        sameMonth = False
        if schedu._month != None:
            schedumonth = schedu._month.split(",")
            sameMonth = [i.strip() for i in schedumonth]
            for month in schedumonth:
                month = month.replace("?", "[0-9]")
                if re.match("^"+month+"$", nowmonth) != None:
                    sameMonth = True
                    break
        if not sameMonth: return
        if schedu._time != None:
            schedutime = schedu._time.split(":")
            schedutime = [i.strip() for i in schedutime]
            scheduH = schedutime[0].replace("?", "[0-9]")
            scheduM = schedutime[1].replace("?", "[0-9]")
            if re.match("^"+scheduH+"$", now_H) == None or re.match("^"+scheduM+"$", now_M) == None:
                return
        schedu.todo()
        
            