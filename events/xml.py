import xml.etree.ElementTree as ET

from events.api import Calendar, CalendarStore, Event, Interval
from datetime import datetime, timedelta
from dateutil.tz import tzlocal


def parse_date(s):
    return datetime.strptime(s, "%Y-%m-%dT%H:%M:%S%z")


class XmlCalendarStore(CalendarStore):
    def __init__(self, folder):
        self.folder = folder

    def all_calendars(self):
        return [Calendar("main")]

    def events(self, cal, start=None, end=None):
        dt = timedelta(weeks=100)
        if start is None:
            start = datetime.now(tzlocal()) - dt
        if end is None:
            end = datetime.now(tzlocal()) + dt

        event_ids = set()
        index = ET.parse(self.folder + "/index.xml").getroot()
        for entry in index:
            e_start = parse_date(entry.attrib["from"])
            e_end = parse_date(entry.attrib["to"])
            if (start < e_start < end) or (start < e_end < end):
                root = ET.parse(self.folder + "/" + entry.attrib["id"] + ".xml").getroot()
                if entry.attrib["id"] in event_ids:
                    continue

                event_ids.add(entry.attrib["id"])
                yield Event(
                    root.find("id").text,
                    root.find("subject").text,
                    root.find("body").text,
                    root.find("from").text,
                    root.find("location").text if root.find("location").text else root.find("room").text,
                    [Interval(parse_date(e.find("start").text), parse_date(e.find("end").text)) for e in
                     root.find("schedule")],
                    [e.text for e in root.find("required-names")],
                    [e.text for e in root.find("optional-names")],
                    {})

