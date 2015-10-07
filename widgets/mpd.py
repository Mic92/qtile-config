# Copyright (c) 2010 matt
# Copyright (c) 2010 Dieter Plaetinck
# Copyright (c) 2010, 2012 roger
# Copyright (c) 2011-2012 Florian Mounier
# Copyright (c) 2011 Mounier Florian
# Copyright (c) 2011 Timo Schmiade
# Copyright (c) 2012 Mikkel Oscar Lyderik
# Copyright (c) 2012, 2014 Tycho Andersen
# Copyright (c) 2012 Craig Barnes
# Copyright (c) 2013 Tao Sauvage
# Copyright (c) 2013 Tom Hunt
# Copyright (c) 2014 Justin Bronder
# Copyright (c) 2015 Mic92
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# -*- coding: utf-8 -*-
# depends on python-mpd

import re

import mpd
import select

from libqtile import utils, pangocffi
from libqtile.widget import base


class Mpd(base.ThreadPoolText):

    """
        An mpd widget.
    """
    orientations = base.ORIENTATION_HORIZONTAL
    defaults = [
        ("foreground_progress", "f0f0f0", "Foreground progress colour"),
        ("foreground", "909090", "Foreground progress colour"),
        ("pause_progress_color", "#a0a0a0", "Font color on pause"),
        ("pause_color", "#505050", "Font color on pause"),
    ]

    # TODO: have this use our config framework
    def __init__(self,
                 host='localhost',
                 port=6600,
                 password=False,
                 fmt_playing="%a - %t [%v%%]",
                 fmt_stopped="Stopped [%v%%]",
                 msg_nc='Mpd off',
                 do_color_progress=True,
                 do_color_pause=False,
                 **config):
        """
            - host: host to connect to
            - port: port to connect to
            - password: password to use
            - fmt_playing, fmt_stopped: format strings to display when playing/paused and when stopped, respectively
            - msg_nc: which message to show when we're not connected
            - do_color_progress: whether to indicate progress in song by altering message color
            - pause_color: font color if paused
            - width: A fixed width, or bar.CALCULATED to calculate the width
            automatically (which is recommended).
        """
        super(Mpd, self).__init__(msg_nc, **config)
        self.host = host
        self.port = port
        self.password = password
        self.fmt_playing, self.fmt_stopped = fmt_playing, fmt_stopped
        self.msg_nc = msg_nc
        self.do_color_progress = do_color_progress
        self.do_color_pause = do_color_pause
        self.inc = 2
        self.add_defaults(Mpd.defaults)
        self.client = mpd.MPDClient()
        self.connected = False
        self.first_poll = True
        self.stop = False

    def finalize(self):
        self.stop = True

        if self.connected:
            try:
                self.client.disconnect()
            except mpd.ConnectionError:
                pass
        base._Widget.finalize(self)

    def connect(self, quiet=False):
        if self.connected:
            return True

        try:
            self.client.connect(host=self.host, port=self.port)
        except Exception:
            if not quiet:
                self.log.exception('Failed to connect to mpd')
            return False

        if self.password:
            try:
                self.client.password(self.password)
            except Exception:
                self.log.warning('Authentication failed.  Disconnecting')
                try:
                    self.client.disconnect()
                except Exception:
                    pass

        self.connected = True
        return True

    def _configure(self, qtile, bar):
        super(Mpd, self)._configure(qtile, bar)
        self.layout = self.drawer.textlayout(
            self.text,
            self.foreground,
            self.font,
            self.fontsize,
            self.fontshadow,
            markup=True
        )

    def to_minutes_seconds(self, stime):
        """Takes an integer time in seconds, transforms it into
        (HH:)?MM:SS. HH portion is only visible if total time is greater
        than an hour.
        """
        if not isinstance(stime, int):
            stime = int(stime)
        mm = stime // 60
        ss = stime % 60
        if mm >= 60:
            hh = mm // 60
            mm = mm % 60
            rv = "{}:{:02}:{:02}".format(hh, mm, ss)
        else:
            rv = "{}:{:02}".format(mm, ss)
        return rv

    def get_artist(self):
        return self.song['artist']

    def get_album(self):
        return self.song['album']

    def get_elapsed(self):
        elapsed = self.status['time'].split(':')[0]
        return self.to_minutes_seconds(elapsed)

    def get_file(self):
        return self.song['file']

    def get_length(self):
        return self.to_minutes_seconds(self.song['time'])

    def get_number(self):
        return str(int(self.status['song']) + 1)

    def get_playlistlength(self):
        return self.status['playlistlength']

    def get_status(self):
        n = self.status['state']
        if n == "play":
            return "▶"
        elif n == "pause":
            return "▮▮"
        elif n == "stop":
            return "◾"

    def get_longstatus(self):
        n = self.status['state']
        if n == "play":
            return "Playing"
        elif n == "pause":
            return "Paused"
        elif n == "stop":
            return "Stopped"

    def get_title(self):
        return self.song['title']

    def get_track(self):
        # This occasionally has leading zeros we don't want.
        return str(int(self.song['track'].split('/')[0]))

    def get_volume(self):
        return self.status['volume']

    def get_single(self):
        if self.status['single'] == '1':
            return '1'
        else:
            return '_'

    def get_repeat(self):
        if self.status['repeat'] == '1':
            return 'R'
        else:
            return '_'

    def get_shuffle(self):
        if self.status['random'] == '1':
            return 'S'
        else:
            return '_'

    formats = {
        'a': get_artist,
        'A': get_album,
        'e': get_elapsed,
        'f': get_file,
        'l': get_length,
        'n': get_number,
        'p': get_playlistlength,
        's': get_status,
        'S': get_longstatus,
        't': get_title,
        'T': get_track,
        'v': get_volume,
        '1': get_single,
        'r': get_repeat,
        'h': get_shuffle,
        '%': lambda x: '%',
    }

    def match_check(self, m):
        try:
            return self.formats[m.group(1)](self)
        except KeyError:
            return "(nil)"

    def do_format(self, string):
        return re.sub("%(.)", self.match_check, string)

    def _status_playing(self):
        text = self.do_format(self.fmt_playing)

        if (self.do_color_progress and self.status and self.status.get(
                'time', None)):
            elapsed, total = self.status['time'].split(':')
            percent = float(elapsed) / float(total)
            progress = int(percent * len(text))

            is_pause = self.status['state'] == 'pause'

            if is_pause:
                color = self.pause_color
                color_progress = self.pause_progress_color
            else:
                color = self.foreground
                color_progress = self.foreground_progress

            s = '<span color="%s">%s</span>' % (
                utils.hex(color_progress),
                pangocffi.markup_escape_text(text[:progress])
            )
            rest = pangocffi.markup_escape_text(text[progress:])
            s += '<span color="%s">%s</span>' % (
                    utils.hex(color),
                    rest
            )

            return s

        else:
            return pangocffi.markup_escape_text(text)

    def _get_status(self):
        try:
            self.status = self.client.status()
            self.song = self.client.currentsong()
        except Exception:
            self.log.exception('Mpd error on update')
            return self.msg_nc

        if self.status['state'] == 'stop':
            return self.do_format(self.fmt_stopped)
        else:
            return self._status_playing()

    def poll(self):
        if not self.connect():
            return

        if self.first_poll:
            self.first_poll = False
            return self._get_status()

        try:
            self.client.send_idle()
            canRead = select.select([self.client], [], [], 5.0)[0]
            if canRead:
                self.client.fetch_idle()
            else:
                self.client.noidle()
        except mpd.ConnectionError:
            self.connected = False
            return self.msg_nc
        except Exception:
            self.log.exception('Error communicating with mpd')
            return

        return self._get_status()

    def button_press(self, x, y, button):
        client = mpd.MPDClient()
        try:
            client.connect(host=self.host, port=self.port)
            status = client.status()
            if button == 3:
                if status['state'] == 'pause':
                    client.play()
                else:
                    client.pause()
            elif button == 4:
                client.setvol(min(int(status['volume']) + self.inc, 100))
            elif button == 5:
                client.setvol(max(int(status['volume']) - self.inc, 0))
        except Exception:
            self.log.exception('Mpd error on click')
        try:
            client.disconnect()
        except mpd.ConnectionError:
            pass
