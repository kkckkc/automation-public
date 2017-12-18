from collections import namedtuple
from contextlib import contextmanager
from datetime import datetime
from dateutil.tz import tzlocal
import re

Interval = namedtuple("Interval", ["start", "end"])


def format_participant(p):
    p = re.sub("CN=(.*)/OU=.*", "\\1", p)
    p = re.sub("(.*)/.*/IBM@IBM[A-Z]+", "\\1", p)
    return p


class CalendarStore(object):
    def all_calendars(self):
        raise NotImplementedError()

    def events(self, calendar, start=None, end=None):
        raise NotImplementedError()

    def add_event(self, cal, event):
        raise NotImplementedError()

    def add_events(self, cal, events):
        for ev in events:
            self.add_event(cal, ev)
        return len(events)

    def remove_event(self, event):
        raise NotImplementedError()

    def remove_events(self, events):
        for ev in events:
            self.remove_event(ev)
        return len(events)

    def commit(self):
        raise NotImplementedError()

    def refresh(self):
        pass

    @contextmanager
    def transaction(self):
        yield
        self.commit()


class Calendar(object):
    def __init__(self, name):
        self.name = name


class Event(object):
    def __init__(self, id, subject, body, owner, location, schedule, required, optional, props):
        self.optional = optional
        self.required = required
        self.location = location
        self.owner = owner
        self.subject = subject
        self.body = body
        self.id = id
        self.props = props or {}

        # No point adding entries to calendar outside of "sane" intervals
        self.schedule = [s for s in schedule if abs((datetime.now(tzlocal()) - s.start).days) < 365]

    def update(self, event, props={}):
        self.optional = props["optional"] if "optional" in props else event.optional
        self.required = props["required"] if "required" in props else event.required
        self.schedule = props["schedule"] if "schedule" in props else event.schedule
        self.location = props["location"] if "location" in props else event.location
        self.owner = props["owner"] if "owner" in props else event.owner
        self.subject = props["subject"] if "subject" in props else event.subject
        self.body = props["body"] if "body" in props else event.body
        self.id = props["id"] if "id" in props else event.id
        self.props = props["props"] if "props" in props else (event.props or {})
        return self

    def __repr__(self):
        items = ("%s = %r" % (k, v) for k, v in self.__dict__.items())
        return "<%s: {%s}>" % (self.__class__.__name__, ', '.join(items))
