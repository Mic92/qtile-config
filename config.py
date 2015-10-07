from libqtile.config import Key, Screen, Drag, Click, Match
import libqtile.config
from libqtile.command import lazy
from libqtile import layout, bar, hook
import libqtile.widget
from libqtile.dgroups import simple_key_binder

import widgets

mod = "mod4"

keys = [
    # Switch between windows in current stack pane
    Key(
        [mod], "k",
        lazy.layout.down()
    ),
    Key(
        [mod], "j",
        lazy.layout.up()
    ),

    Key([mod], "f", lazy.window.toggle_floating()),

    # Move windows up or down in current stack
    Key(
        [mod, "control"], "k",
        lazy.next_layout()
    ),
    Key(
        [mod, "control"], "j",
        lazy.prev_layout()
    ),

    # Switch window focus to other pane(s) of stack
    Key(
        [mod], "space",
        lazy.layout.next()
    ),

    # Swap panes of split stack
    Key(
        [mod, "shift"], "space",
        lazy.layout.rotate()
    ),

    # Toggle between split and unsplit sides of stack.
    # Split = all windows displayed
    # Unsplit = 1 window displayed, like Max layout, but still with
    # multiple stack panes
    Key(
        [mod, "shift"], "Return",
        lazy.layout.toggle_split()
    ),
    Key([mod], "Return", lazy.spawn("urxvt")),

    # Toggle between different layouts as defined below
    Key([mod], "Tab", lazy.nextlayout()),
    Key([mod], "w", lazy.window.kill()),

    Key([mod, "control"], "r", lazy.restart()),
    Key([mod, "control"], "q", lazy.shutdown()),
    Key([mod], "r", lazy.spawncmd()),
    #Key([], "XF86AudioRaiseVolume", )
    #Key([], "XF86AudioLowerVolume", )
    #Key([], "XF86AudioMute", )
    Key([], "XF86MonBrightnessUp", lazy.spawn("xbacklight -inc 10")),
    Key([], "XF86MonBrightnessDown", lazy.spawn("xbacklight -dec 10")),
    Key(["shift"], "space", lazy.spawn("mpc toggle")),
]


class Group(libqtile.config.Group):
    """
    Group with custom keys
    """
    def __init__(self, name, key, *args, **kwargs):
        super(Group, self).__init__(name, *args, **kwargs)
        self.key = key

groups = [
        Group('1:web', 1,
            init=True,
            persist=False,
            exclusive=True,
            position=1,
            matches=[Match(wm_class=['Chromium-browser', 'Minefield', 'Firefox'], role=['browser'])]),
        Group('2:dev', 2,
            init=True,
            persist=False,
            position=2,
            exclusive=True,
            matches=[Match(wm_class=['urxvt', 'URxvt'])]),
        Group('3:im', 3,
            init=False,
            persist=False,
            position=3,
            exclusive=True,
            matches=[Match(wm_class=['gajim', 'Gajim'])]),
        Group('4:mail', 4,
            init=False,
            persist=False,
            position=4,
            exclusive=True,
            matches=[Match(wm_class=['Claws-mail', 'Thunderbird'])]),
        Group('5:doc', 5,
            init=False,
            persist=False,
            position=5,
            matches=[Match(wm_class=["Evince", "GVim", "Keepassx", "libreoffice"])]),
        Group('g:pod', 'g',
            init=False,
            persist=False,
            matches=[Match(wm_class=["Gpodder"])]),
        Group('v:ideo', 'v',
            init=False,
            persist=False,
            matches=[Match(wm_class=["MPlayer", "VLC", "Smplayer", "mpv"])]),
        Group('p:manfm', 'p',
            init=False,
            persist=False,
            matches=[Match(wm_class=["pcmanfm", "Pcmanfm"])]),
]

for i in groups:
    # mod1 + letter of group = switch to group
    keys.append(
        Key([mod], str(i.key), lazy.group[i.name].toscreen())
    )

    # mod1 + shift + letter of group = switch to & move focused window to group
    keys.append(
        Key([mod, "shift"], str(i.key), lazy.window.togroup(i.name))
    )

border = dict(
    border_normal='#808080',
    border_width=0,
)

layouts = [
    layout.Max(),
    layout.Stack(num_stacks=2),
    layout.Tile(**border),
    layout.RatioTile(**border),
    layout.MonadTall(**border),
]

widget_defaults = dict(
    font='Noto',
    fontsize=16,
    padding=3,
)

battery_default = dict(energy_now_file='charge_now',
    energy_full_file='charge_full',
    power_now_file='current_now',
    update_delay=5,
    foreground="7070ff",)
battery1 = battery_default.copy()
battery1.update(dict(battery_name='BAT0'))
battery2 = battery_default.copy()
battery2.update(dict(battery_name='BAT1'))

battery1_widget = libqtile.widget.Battery(**battery1)
battery1_icon   = libqtile.widget.BatteryIcon(**battery1)
seperator       = libqtile.widget.TextBox("|")
battery2_widget = libqtile.widget.Battery(**battery2)
battery2_icon   = libqtile.widget.BatteryIcon(**battery2)

mpd_widget = widgets.Mpd(fmt_playing="%s %a - %t: %e/%l",
        do_color_pause=True)

clock_widget = libqtile.widget.Clock(format='%Y-%m-%d %a %H:%M %p')
cpu_graph = libqtile.widget.CPUGraph(
        samples=50,
        line_width=1,
        width=50,
        graph_color='FF2020',
        fill_color='C01010')
memory_widget = widgets.Memory()
net_graph = libqtile.widget.NetGraph(
        samples=50,
        line_width=1,
        width=50,
        interface="wlp3s0",
        graph_color='22FF44',
        fill_color='11AA11')

top_widgets = [
    libqtile.widget.GroupBox(),
    libqtile.widget.Prompt(),
    libqtile.widget.TaskList(),
    battery1_icon,
    battery1_widget,
    seperator,
    battery2_icon,
    battery2_widget,
    clock_widget,
    #widget.Volume(update_interval=2, emoji=True),
    libqtile.widget.Systray()]

bottom_widgets = [
    #widget.Notify(foreground="FF0000", fontsize=14),
    libqtile.widget.TextBox("C:", name="default"),
    cpu_graph,
    libqtile.widget.TextBox("M:", name="default"),
    memory_widget,
    libqtile.widget.TextBox("N:", name="default"),
    net_graph,
    mpd_widget
]
screens = [
    Screen(
        top=bar.Bar(top_widgets, 30),
        bottom=bar.Bar(bottom_widgets, 30),
    ),
]

@hook.subscribe.client_managed
def focus_client(window):
    window.qtile.currentScreen.setGroup(window.group)
    window.group.focus(window, False)

# Drag floating layouts.
mouse = [
    Drag([mod], "Button1", lazy.window.set_position_floating(),
         start=lazy.window.get_position()),
    Drag([mod], "Button3", lazy.window.set_size_floating(),
         start=lazy.window.get_size()),
    Click([mod], "Button2", lazy.window.bring_to_front())
]
dgroups_key_binder = simple_key_binder(mod)

#dgroups_key_binder = None
dgroups_app_rules = []
main = None
follow_mouse_focus = True
bring_front_click = False
cursor_warp = False
floating_layout = layout.Floating()
auto_fullscreen = True

# XXX: Gasp! We're lying here. In fact, nobody really uses or cares about this
# string besides java UI toolkits; you can see several discussions on the
# mailing lists, github issues, and other WM documentation that suggest setting
# this string if your java app doesn't work correctly. We may as well just lie
# and say that we're a working one by default.
#
# We choose LG3D to maximize irony: it is a 3D non-reparenting WM written in
# java that happens to be on java's whitelist.
wmname = "LG3D"
