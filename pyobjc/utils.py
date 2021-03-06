import Foundation
from dateutil.parser import parse
from Foundation import NSUserNotification, NSUserNotificationCenter

DATE_FORMAT = "%Y-%m-%d %H:%M:%S %z"


def datetime_to_nsdate(dt):
    if not dt.tzinfo:
        return Foundation.NSDate.dateWithString_("{} +0000".format(dt.strftime("%Y-%m-%d %H:%M:%S")))
    else:
        return Foundation.NSDate.dateWithString_(dt.strftime(DATE_FORMAT))


def nsdate_to_datetime(nsd):
    return parse(nsd.__str__())


def safe_call(r):
    res, err = r
    if not res:
        raise Exception("Failed {}".format(err.localizedDescription()))
    return res


def notify(title, text):
    notification = NSUserNotification.alloc().init()
    notification.setTitle_(str(title))
    notification.setInformativeText_(str(text))
    NSUserNotificationCenter.defaultUserNotificationCenter().scheduleNotification_(notification)
