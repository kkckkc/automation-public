if __name__ == '__main__':
	import sys
	sys.path.append('..')

from events.api import CalendarStore, Calendar, Event, Interval
from datetime import datetime, timedelta
from dateutil.tz import tzlocal
from dateutil.parser import parse
from objc_util import *

import sys
import time
import calendar as pysyscal
import ctypes


EKEventStore = ObjCClass('EKEventStore')
EKEvent = ObjCClass('EKEvent')
NSDate = ObjCClass('NSDate')

AUTHORIZATION_STATUS_NOT_DETERMINED = 0
AUTHORIZATION_STATUS_DENIED = 2
AUTHORIZATION_STATUS_AUTHORIZED = 3

class IosCalendarStore(CalendarStore):
	def __init__(self):
		auth_status = EKEventStore.authorizationStatusForEntityType_(0)
		if auth_status == AUTHORIZATION_STATUS_AUTHORIZED:
			self.objc_object = EKEventStore.alloc().init()
		elif auth_status == AUTHORIZATION_STATUS_NOT_DETERMINED:
			self.__request_access()
			self.objc_object = EKEventStore.alloc().init()
		elif auth_status == AUTHORIZATION_STATUS_DENIED:
			console.hud_alert('Access to calendar denied.')

	def __request_access(self):
		def completion_handler(_cmd, success, error_ptr):
			error = ObjCInstance(error_ptr)
			print(success)
			print(error)
			
		completion_handler_block = ObjCBlock(
			completion_handler, restype=None, 
			argtypes=[c_void_p, c_bool, c_void_p])
	
		EKEventStore.new().requestAccessToEntityType_completion_(
			0, completion_handler_block)
	
	def all_calendars(self):
		objc_calendars = self.objc_object.calendarsForEntityType_(0)
		return [IosCalendar(cal) for cal in objc_calendars]

	def events(self, calendar, start=None, end=None):
		dt = timedelta(weeks=100)
		if start is None:
			start = datetime.now(tzlocal()) - dt
		if end is None:
			end = datetime.now(tzlocal()) + dt
	
		predicate = self.objc_object.predicateForEventsWithStartDate_endDate_calendars_(
			to_nsdate(start), to_nsdate(end), [calendar.objc_object])
		events_matching_predicate = self.objc_object.eventsMatchingPredicate_(predicate)
		if events_matching_predicate is None:
			return []
		else:
			return map(lambda e: IosEvent(e), events_matching_predicate)

class IosEvent(Event):
	def __init__(self, evt):
		super().__init__(
				evt.eventIdentifier(), 
				evt.title(), 
				evt.notes(), 
				None if not evt.organizer() else evt.organizer().emailAddress(),
				evt.location(), 
				[Interval(from_nsdate(evt.startDate()), from_nsdate(evt.endDate()))], 
				[str(p.name()) for p in evt.attendees()] if evt.attendees() else None,
				None, 
				None)
		self.objc_object = evt
	
class IosCalendar(Calendar):
	def __init__(self, cal):
		super().__init__(str(cal.title()))		
		self.identifier = str(cal.calendarIdentifier())
		self.objc_object = cal	
	
def from_nsdate(nsdate):
	return parse(str(nsdate))
			
def to_nsdate(date):
	date_as_tuple = date.timetuple()
	timestamp = pysyscal.timegm(date_as_tuple)
	return NSDate.alloc().initWithTimeIntervalSince1970_(timestamp)
	
			
if __name__ == '__main__':
	store = IosCalendarStore()
	for cal in store.all_calendars():
		print("***********************")
		print(cal.name)
		for evt in store.events(cal, parse("2018-01-29 08:00"), parse("2018-01-29 19:00")):
			print(evt.id)
			print(evt.subject)
			print(evt.body)
			print(evt.owner)
			print(evt.location)
			print(evt.schedule)
			print(evt.required)
			print("---------")

