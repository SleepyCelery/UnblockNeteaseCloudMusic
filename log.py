from datetime import datetime


def timeformat():
    time_str = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    return time_str


def write_log(info):
    with open('NeteaseMusicProxyLog.txt', mode='a+') as logfile:
        logfile.write("{} {}{}".format(timeformat(), info,'\n'))


