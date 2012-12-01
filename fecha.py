import datetime
import time

def mkDateTime(dateString,strFormat="%Y-%m-%d"):
        # Expects "YYYY-MM-DD" string
        # returns a datetime object
        eSeconds = time.mktime(time.strptime(dateString,strFormat))
        return datetime.datetime.fromtimestamp(eSeconds)

def formatDate(dtDateTime,strFormat="%Y-%m-%d"):
        # format a datetime object as YYYY-MM-DD string and return
        return dtDateTime.strftime(strFormat)

class fecha:
        def mkDateTime(dateString,strFormat="%Y-%m-%d"):
                # Expects "YYYY-MM-DD" string
                # returns a datetime object
                eSeconds = time.mktime(time.strptime(dateString,strFormat))
                return datetime.datetime.fromtimestamp(eSeconds)

        def getNow(self):
                return datetime.datetime.now()

        def getUltimoDia(self,dtDateTime):
                dYear = dtDateTime.strftime("%Y")        #get the year
                dMonth = str(int(dtDateTime.strftime("%m"))%13)#get next month, watch rollover
                dDay = "1"                               #first day of next month
                nextMonth = mkDateTime("%s-%s-%s"%(dYear,dMonth,dDay))#make a datetime obj for 1st of next month
                delta = datetime.timedelta(seconds=1)    #create a delta of 1 second
                return nextMonth - delta                 #subtract from nextMonth and return

        def getPrimerDia(self,dtDateTime):
                #what is the first day of the current month
                #format the year and month + 01 for the current datetime, then form it back
                #into a datetime object
                return mkDateTime(formatDate(dtDateTime,"%Y-%m-01"))
