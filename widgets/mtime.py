import time
import os

from libqtile.widget import base


class Mtime(base.InLoopPollText):
    orientations = base.ORIENTATION_HORIZONTAL

    def __init__(self, **config):
        base.InLoopPollText.__init__(self, **config)
        self.file = "/var/lib/last-backup"
        self.threshold = 12 * 60 * 60

    def poll(self):
        try:
            mtime = os.path.getmtime(self.file)
        except FileNotFoundError:
            return "No Backup"
        now = time.mktime(time.localtime())
        if max(now - mtime, 0) > self.threshold:
            return "Backup time"
        return "-"
