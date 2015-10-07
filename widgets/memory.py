import re
from libqtile.widget import base


def get_meminfo():
    val = {}
    with open('/proc/meminfo') as file:
        for line in file:
            key, tail = line.split(':')
            uv = tail.split()
            val[key] = int(int(uv[0]) / 1000)
    return val


class Memory(base.InLoopPollText):
    """Displays a memory usage graph."""
    orientations = base.ORIENTATION_HORIZONTAL
    defaults = [
        ("format", "%{MemFree}M/%{MemTotal}M", "see /proc/meminfo for fields")
    ]

    def __init__(self, **config):
        super(Memory, self).__init__(**config)
        self.add_defaults(Memory.defaults)

    def poll(self):
        mem = get_meminfo()

        def replace(m):
            return str(mem.get(m.group(1), "(nil)"))
        return re.sub("%{([^}]+)}", replace, self.format)
