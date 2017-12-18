import subprocess

from events.xml import XmlCalendarStore


class NotesCalendarStore(XmlCalendarStore):
    def __init__(self, folder, java, notes_extractor, notes_server, notes_password):
        super().__init__(folder)
        self.notes_password = notes_password
        self.notes_server = notes_server
        self.java = java
        self.notes_extractor = notes_extractor
        self.refresh()

    def refresh(self):
        notes_path = "/Applications/IBM Notes.app/Contents/MacOS"
        ext_dir = "{}/jvm/lib/ext/".format(notes_path)

        classpath = ["{}{}".format(ext_dir, jar) for jar in ["Notes.jar", "njempcl.jar", "websvc.jar"]] + [
            self.notes_extractor]

        command = [
            self.java,
            "-Djava.library.path={}".format(notes_path),
            "-Djava.ext.dirs={}/ndext:{}".format(notes_path, ext_dir),
            "-Dfile.encoding=UTF-8",
            "-classpath", ":".join(classpath),
            "kkckkc.ExtractCalendar",
            self.folder,
            self.notes_server,
            self.notes_password
        ]

        subprocess.run(command, shell=False, check=True,
                       env={"PATH": notes_path, "DYLD_LIBRARY_PATH": notes_path, "NOTESBIN": notes_path})

