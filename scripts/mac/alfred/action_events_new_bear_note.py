import webbrowser

from apps.bear import add_text, add_file, meeting_note
from datetime import datetime, timedelta
from dateutil.tz import tzlocal
from events.xml import XmlCalendarStore
import argparse

parser = argparse.ArgumentParser(description='Generate bear meeting note for event')
parser.add_argument('--folder', required=True)
parser.add_argument('--id', required=True)
parser.add_argument('--action', required=True)
parser.add_argument('--data', required=True)
args = parser.parse_args()

folder = args.folder
id = args.id
action = args.action
data = args.data


target = XmlCalendarStore(folder)
target_cal = next(c for c in target.all_calendars() if c.name == "main")

start = datetime.now(tzlocal()) - timedelta(hours=10)
end = datetime.now(tzlocal()) + timedelta(hours=10)
event = next(e for e in target.events(target_cal, start, end) if e.id == id)

if action == "new":
    additional_tags = []
    if event.contains("ikea") or event.contains("IKEA"):
        additional_tags.append("ikea")
    webbrowser.open(add_text(event.subject, meeting_note(event, additional_tags)))
elif action == "open":
    webbrowser.open(add_text(event.subject, ""))
elif action == 'action':
    webbrowser.open(add_text(event.subject, "- " + data.strip() + "\n"))
elif action == 'file':
    webbrowser.open(add_file(event.subject, data))

