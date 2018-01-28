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
AUTHORIZATION_STATUS_RESTRICTED = 1
AUTHORIZATION_STATUS_DENIED = 2
AUTHORIZATION_STATUS_AUTHORIZED = 3

class IosCalendarStore(CalendarStore):
	def __init__(self):
		auth_status = EKEventStore.authorizationStatusForEntityType_(0)
		if auth_status == AUTHORIZATION_STATUS_AUTHORIZED:
			self.event_store = EKEventStore.alloc().init()
		elif auth_status == AUTHORIZATION_STATUS_NOT_DETERMINED:
			self.request_access()
			self.event_store = EKEventStore.alloc().init()
		elif auth_status == AUTHORIZATION_STATUS_DENIED:
			console.hud_alert('Access to calendar denied. open settings to allow')

	def request_access(self):
		def completion_handler(_cmd, success, error_ptr):
			error = ObjCInstance(error_ptr)
			if debug:
				print(success)
				print(error)
			
		completion_handler_block = ObjCBlock(completion_handler, restype=None, argtypes=[c_void_p, c_bool, c_void_p])
	
		EKEventStore.new().requestAccessToEntityType_completion_(0, completion_handler_block)
	
	def all_calendars(self):
		objc_calendars = self.event_store.calendarsForEntityType_(0)
		calendars = []
		for cal in objc_calendars:
			calendar = IosCalendar(str(cal.title()))
			calendar.identifier = str(cal.calendarIdentifier())
			calendar.objc_object = cal
			calendars.append(calendar)
		return calendars

	def nsdate_from_python_date(self, date):
		date_as_tuple = date.timetuple()
		timestamp = pysyscal.timegm(date_as_tuple)
		return NSDate.alloc().initWithTimeIntervalSince1970_(timestamp)
	
	def events(self, calendar, start=None, end=None):
		dt = timedelta(weeks=1)
		if start is None:
			start = datetime.now(tzlocal()) - dt
		if end is None:
			end = datetime.now(tzlocal()) + dt
	
		predicate = self.event_store.predicateForEventsWithStartDate_endDate_calendars_(self.nsdate_from_python_date(start), self.nsdate_from_python_date(end), [calendar.objc_object])
		events_matching_predicate = self.event_store.eventsMatchingPredicate_(predicate)
		if events_matching_predicate is None:
			return []
		else:
			objc_events = list(events_matching_predicate)
		
		events = map(lambda e: IosEvent(e), objc_events)
		return events
	

class IosEvent(Event):
	def __init__(self, evt):
		super().__init__(
				evt.eventIdentifier(), 
				evt.title(), 
				evt.notes(), 
				None if not evt.organizer() else evt.organizer().emailAddress(),
				evt.location(), 
				[Interval(
					self.python_date_from_nsdate(evt.startDate()),
					self.python_date_from_nsdate(evt.endDate()))
				], 
				[p.name().__str__() for p in evt.attendees()] if evt.attendees() else None,
				None, 
				None)

	def python_date_from_nsdate(self, nsdate):
		return parse(nsdate.__str__())
	
class IosCalendar(Calendar):
	def __init__(self, name):
		super().__init__(name)		
		
	def __repr__(self):
		return "IosCalendar<{}, {}>".format(self.name, self.identifier)
	
	
if __name__ == '__main__':
	store = IosCalendarStore()
	for cal in store.all_calendars():
#		if cal.name == 'Magnus Johansson - My Calendar':
		print("***********************")
		print(cal)
		for evt in store.events(cal, parse("2018-01-29 08:00"), parse("2018-01-29 19:00")):
			print(evt.id)
			print(evt.subject)
			print(evt.body)
			print(evt.owner)
			print(evt.location)
			print(evt.schedule)
			print(evt.required)
			print("---------")

