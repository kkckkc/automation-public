import EventKit
import json

from events.api import Calendar, CalendarStore, Event, Interval
from datetime import datetime, timedelta
from pyobjc.utils import datetime_to_nsdate, nsdate_to_datetime, safe_call
from dateutil.tz import tzlocal


DATE_FORMAT = "%Y-%m-%d %H:%M:%S %z"
DELIMITER = "\n@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"


class PyObjcCalendarStore(CalendarStore):
    def __init__(self):
        self.store = EventKit.EKEventStore.new()

    def all_calendars(self):
        return [PyObjcCalendar(c) for c in self.store.allCalendars()]

    def events(self, cal, start=None, end=None):
        dt = timedelta(weeks=100)
        if start is None:
            start = datetime.now(tzlocal()) - dt
        if end is None:
            end = datetime.now(tzlocal()) + dt

        predicate = self.store.predicateForEventsWithStartDate_endDate_calendars_(datetime_to_nsdate(start), datetime_to_nsdate(end), [cal.obj])
        return [PyObjcEvent(e) for e in self.store.eventsMatchingPredicate_(predicate)]

    def add_event(self, cal, e):
        def change_attribute(obj, param, value):
            if obj[param] != value:
                obj[param] = value
                return True
            return False

        assert len(e.schedule) == 1, "Only events with one schedule supported"

        if type(e) == PyObjcEvent:
            event = e.obj
        else:
            event = EventKit.EKEvent.eventWithEventStore_(self.store)

        e.props['_required'] = e.required
        e.props['_optional'] = e.optional
        e.props['_owner'] = e.owner

        changed = change_attribute(event._, "calendar", cal.obj) | \
                  change_attribute(event._, "title", e.subject) | \
                  change_attribute(event._, "location", e.location) | \
                  change_attribute(event._, "notes", (e.body or "") + DELIMITER + json.dumps(e.props)) | \
                  change_attribute(event._, "startDate", datetime_to_nsdate(e.schedule[0].start)) | \
                  change_attribute(event._, "endDate", datetime_to_nsdate(e.schedule[0].end))

        if changed:
            safe_call(self.store.saveEvent_span_commit_error_(event, 0, False, None))

        return e if type(e) == PyObjcEvent else PyObjcEvent(event)

    def remove_event(self, event):
        safe_call(self.store.removeEvent_span_commit_error_(event.obj, 0, False, None))

    def commit(self):
        safe_call(self.store.commit_(None))


class PyObjcCalendar(Calendar):
    def __init__(self, obj):
        super().__init__(obj._.title)
        self.obj = obj


class PyObjcEvent(Event):
    def __init__(self, obj):
        super().__init__(
            obj._.UUID,
            obj._.title,
            obj._.notes,
            None if not obj._.organizer else obj._.organizer._.emailAddress,
            obj._.location,
            [Interval(nsdate_to_datetime(obj._.startDate), nsdate_to_datetime(obj._.endDate))],
            [p._.name for p in obj._.attendees] if obj._.attendees else None,
            None,
            self._parse_properties(obj._.notes))
        self.obj = obj
        self.owner = self.props['_owner'] if '_owner' in self.props and self.owner is None else self.owner
        self.optional = self.props['_optional'] if '_optional' in self.props and self.optional is None else self.optional
        self.required = self.props['_required'] if '_required' in self.props and self.required is None else self.required

    def _parse_properties(self, notes):
        if notes is None:
            return {}
        arr = notes.split(DELIMITER)
        if len(arr) == 1:
            return {}
        else:
            try:
                return json.loads(arr[1])
            except json.decoder.JSONDecodeError:
                return {}

    def __repr__(self):
        items = ("%s = %r" % (k, v) for k, v in self.__dict__.items())
        return "<%s: {%s}>" % (self.__class__.__name__, ', '.join(items))
