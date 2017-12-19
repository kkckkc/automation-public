from datetime import datetime


DATE_FORMAT = "%Y-%m-%d %H:%M:%S %z"

def log(s):
    print("{} - {}".format(datetime.now().strftime(DATE_FORMAT), s))
