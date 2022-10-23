#!/bin/python
import pywal
import yaml
import os
import sys
import getopt

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
    wal_data = {}
    wal_data["wallpaper"] = "None"
    wal_data["alpha"] = pywal.theme.util.Color.alpha_num

    wal_data["special"] = {
        "foreground": alacritty_theme["primary"]["foreground"],
        "background": alacritty_theme["primary"]["background"],
        "cursor": "cursor" in alacritty_theme and alacritty_theme["cursor"]["cursor"] or alacritty_theme["bright"]["yellow"]
    }
    normal_colors = alacritty_theme["normal"]
    bright_colors = alacritty_theme["bright"]
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
