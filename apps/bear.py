import base64
import os

from urllib.parse import quote
from events.api import format_participant


def meeting_note(event, additional_tags):
    datestr = event.schedule[0].start.strftime("%Y-%m-%d %H:%M") + " - " + event.schedule[0].end.strftime("%H:%M")
    participants = "\t* " + "\n\t* ".join(map(format_participant, [event.owner] + event.required + event.optional))

    return f"""#meeting {" ".join(map(lambda t: "#" + t, additional_tags))}

## Info
ID: {event.id}
Date: {datestr}
Participants:
{participants}

## Notes
"""


def add_text(title, text):
    return "bear://x-callback-url/add-text?exclude_trashed=yes&text={}&title={}&mode=append".format(quote(text), quote(title))


def add_file(title, file):
    filename = os.path.basename(file)
    with open(file, "rb") as f:
        read_data = f.read()
    data = base64.b64encode(read_data)

    return "bear://x-callback-url/add-file?exclude_trashed=yes&filename={}&file={}&title={}&mode=append".format(
        quote(filename), quote(data), quote(title))
