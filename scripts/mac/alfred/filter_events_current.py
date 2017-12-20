import json

from datetime import datetime, timedelta
from dateutil.tz import tzlocal
from events.xml import XmlCalendarStore
import argparse

parser = argparse.ArgumentParser(description='Get current events from Apple Calendar')
parser.add_argument('--folder', required=True)
folder = parser.parse_args().folder

target = XmlCalendarStore(folder)
target_cal = next(c for c in target.all_calendars() if c.name == "main")

start = datetime.now(tzlocal()) - timedelta(hours=4)
end = datetime.now(tzlocal()) + timedelta(hours=2)
target_events = target.events(target_cal, start, end)

items = []
for e in sorted(target_events, key=lambda e: abs(datetime.now(tzlocal()) - e.schedule[0].start)):
    items.append({"uuid": e.id,
                  "title": e.subject,
                  "subtitle": "{} - {}, {}".format(
                      e.schedule[0].start.strftime("%H:%M"), e.schedule[0].end.strftime("%H:%M"), e.location),
                  "arg": e.id,
                  "icon": {"type": "file", "path": "/Applications/Calendar.app/Contents/Resources/App.icns"}
                  })


print(json.dumps({"items": items}))

