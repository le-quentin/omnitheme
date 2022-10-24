#!/bin/python
import pywal
import yaml
import os
import sys
import getopt

"""
TODO
- -c/--colours primary,secondary option (i.e. omnitheme -c green,cyan theme_name => apply the theme with green primary and cyan secondary). The given colours will be used as background, and the foreground should be picked between black and white depending on highest contrast (compute it).
- -a/--automatic => automatically picks primary and secondary. Algorithm TBD. Idea: sort by contrast to the background, and pick the primary closest to "ideal contrast". Then do the same with the secondary, ideal contrast to primary this time (with contrast to background in a given range)
- Interactive mode : display all themes in the terminal, and apply the theme as a preview on the fly (i.e. after 1s stop on the theme name). On cancel, rollback to previous theme (=> need to store current theme somewhere in cache first)
- Random mode : picks a random theme in a given list (as a value if given, if not read from a config file => handle a omnitheme.conf) 

omnitheme_schedule wrapper:
runs omnitheme with given options at certains times (with a cron?). You provide a config file and the cli is just there to manage the cron (create, remove, update with new config file).
The config file should give direct access to cron parameters, and maybe propose a few helpers like AM, PM, MONDAY, TUESDAY...

Could be handled with a -s/--schedule [config] option.
If a schedule is enabled, at any execution time, the restore mode (omnitheme -r) should refresh the theme depending on the time of execution.
"""

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader


HOME = os.environ.get('HOME')
TERMINAL_ANSI_COLORS = ["black","red","green","yellow","blue","magenta","cyan","white"]

def get_alacritty_colours(theme_path):
    with open(theme_path) as f:
        file_str = ''.join(f.readlines())
    file_str = file_str.replace("0x", "#")
    alacritty_theme=yaml.load(file_str, Loader);
    return alacritty_theme["colors"]


def alacritty_to_wal(alacritty_theme):
    normal_colors = alacritty_theme["normal"]
    bright_colors = alacritty_theme["bright"]
    wal_data = {}
    wal_data["wallpaper"] = "None"
    wal_data["alpha"] = pywal.theme.util.Color.alpha_num

    wal_data["special"] = {
        "background": alacritty_theme["primary"]["background"],
        "background_variant": normal_colors["black"],
        "foreground": alacritty_theme["primary"]["foreground"],
        "cursor": "cursor" in alacritty_theme and alacritty_theme["cursor"]["cursor"] or alacritty_theme["bright"]["yellow"],

        "primary_background": bright_colors["green"],
        "primary_foreground": normal_colors["black"],
        "secondary_background": bright_colors["cyan"],
        "secondary_foreground": normal_colors["black"]
    }
    wal_data["colors"] = { }
    for i, color  in enumerate(TERMINAL_ANSI_COLORS):
        wal_data["colors"][f"color{i}"] = normal_colors[color]
        wal_data["colors"][f"color{8+i}"] = bright_colors[color]
    return wal_data

def usage():
    print("""
omnitheme.py [option]... [theme_name]

theme_name is the name of a colour theme yml file in your Alacritty themes dir (without the extensions).

option is one or many of:
    -r, --restore           Apply the currently cached theme, aka the last one you loaded. Useful to restore theme after loading the window manager. Doesn't require a theme_name argument.
    -h, --help              Display this help.
          """)

try:
    opts, args = getopt.getopt(sys.argv[1:],"rh",["restore","help"])
except getopt.GetoptError:
    usage()
    sys.exit(2)

RESTORE_MODE = False
THEME_NAME = ""

for opt, value in opts:
    if opt in ["-h", "--help"]:
        usage()
        sys.exit(0)
    elif opt in ["-r", "--restore"]:
        RESTORE_MODE = True

# Restore mode, reload env and exit
if RESTORE_MODE:
    pywal.reload.env()
    sys.exit(0)

# Normal mode, read from alacritty theme
if len(args) != 1:
    print("You must provide a theme name")
    usage()
    sys.exit(2)
theme_name = args[0]
alacritty_colours = get_alacritty_colours(f'{HOME}/.config/alacritty/themes/{theme_name}.yml')
colors = alacritty_to_wal(alacritty_colours)

pywal.export.every(colors, f"{HOME}/.cache/wal")

pywal.reload.env()
