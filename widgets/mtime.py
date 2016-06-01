import time
import os

from libqtile.widget import base


class Mtime(base.InLoopPollText):
    orientations = base.ORIENTATION_HORIZONTAL
    defaults = [
        ("file", "/etc/resolv.conf", "tile to check"),
        ("time_threshold",
         12 * 60 * 60,
         "Time in seconds to wait before showing text"),
        ("text_older_threshold",
         "File is not updated",
         "Text to show if file is older then threshold"),
        ("text_younger_threshold",
         " ",
         "Text to show if file is newer then threshold"),
        ("text_file_not_found",
         "File not found",
         "Text if file is not found")
    ]

    def __init__(self, **config):
        base.InLoopPollText.__init__(self, **config)
        self.add_defaults(self.defaults)

    def poll(self):
        try:
            mtime = os.path.getmtime(self.file)
        except FileNotFoundError:
            return self.text_file_not_found
        now = time.mktime(time.localtime())
        if max(now - mtime, 0) > self.time_threshold:
            return self.text_older_threshold
        return self.text_younger_threshold
