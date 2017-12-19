import argparse

from datetime import datetime
from events.api import Event
from events.notes import NotesCalendarStore
from events.pyobjc import PyObjcCalendarStore

# To request access to calendar
from CalendarStore import CalCalendarStore
store = CalCalendarStore.defaultCalendarStore()


parser = argparse.ArgumentParser(description='Sync Notes and Apple Calendar')
parser.add_argument('--output', required=True)
parser.add_argument('--clean', action="store_const", const=True, default=False)
parser.add_argument('--calendar', required=True)
parser.add_argument('--java', required=True)
parser.add_argument('--notes_extractor', required=True)
parser.add_argument('--notes_server', required=True)
parser.add_argument('--notes_password', required=True)

args = parser.parse_args()


DATE_FORMAT = "%Y-%m-%d %H:%M:%S %z"


def log(s):
    print("{} - {}".format(datetime.now().strftime(DATE_FORMAT), s))


# Setup source and targets
source = NotesCalendarStore(args.output, args.java, args.notes_extractor, args.notes_server, args.notes_password)
source_cal = next(c for c in source.all_calendars())

target = PyObjcCalendarStore()
target_cal = next(c for c in target.all_calendars() if c.name == args.calendar)

log("Getting Events from Target - getting events from {}".format(args.calendar))
target_events = target.events(target_cal)
log("Getting Events from Target - {} events found".format(len(target_events)))

# Delete all to get clean run
if args.clean or len([e for e in target_events if "urn" not in e.props]) > 0:
    log("Cleaning Target - Cleaning all events in {} ({} events)".format(args.calendar, len(target_events)))
    with target.transaction():
        target.remove_events(target_events)
        target_events = []
    log("Cleaning Target - Cleaning events done")

# Map all elements in target by urn
target_events_by_urn = {e.props['urn']: e for e in target_events if "urn" in e.props}

# Add missing events and update existing
log("Adding Events to Target - start")
added, updated = 0, 0
source_events_by_urn = {}
with target.transaction():
    for xe in source.events(source_cal):
        for sch in xe.schedule:
            urn = "urn:{}/{}".format(xe.id, sch.start.strftime(DATE_FORMAT))
            props = {"urn": urn}
            if urn in target_events_by_urn:
                ev = target_events_by_urn[urn].update(xe, {"schedule": [sch], "props": props})
                updated += 1
            else:
                ev = Event(xe.id, xe.subject, xe.body, xe.owner, xe.location, [sch], xe.required, xe.optional, props)
                added += 1
            target.add_event(target_cal, ev)
            source_events_by_urn[urn] = ev
log("Adding Events to Target - added {} and updated {} events".format(added, updated))

# Remove events removed from source
log("Deleting Events from Target - start")
with target.transaction():
    number_of_deletes = target.remove_events(
        [target_events_by_urn[urn] for urn in target_events_by_urn.keys() if urn not in source_events_by_urn])
    log("Deleting Events from Target - deleted {} events".format(number_of_deletes))

