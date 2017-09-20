# Terminal Stuff
# Use keys from color_codes array below to put colors into text
# Use {{x,y; to put a text position into your text
from __future__ import print_function

import colorama


import sys

from colorama import init, Fore, Back, Style
init()

TERM_WIDTH = 80
TERM_HEIGHT = 24

CSI = "\x1b["
CLEAR_SCREEN = CSI + "2J"
RESET_COLOR = CSI + "0"

BOLD = "1"
ITALICS = "3"
UNDERLINE = "4"
INVERSE = "7"
STRIKETHROUGH = "9"

BOLD_OFF="22"
ITALICS_OFF="23"
UNDERLINE_OFF="24"
INVERSE_OFF="27"
STRIKETHROUGH_OFF="29"

NORMAL_ONLY = BOLD_OFF+";"+ITALICS_OFF+";"+UNDERLINE_OFF+";"+INVERSE_OFF+";"+STRIKETHROUGH_OFF
BOLD_ONLY = BOLD+";"+ITALICS_OFF+";"+UNDERLINE_OFF+";"+INVERSE_OFF+";"+STRIKETHROUGH_OFF
ITALICS_ONLY = BOLD_OFF+";"+ITALICS+";"+UNDERLINE_OFF+";"+INVERSE_OFF+";"+STRIKETHROUGH_OFF
UNDERLINE_ONLY = BOLD_OFF+";"+ITALICS_OFF+";"+UNDERLINE+";"+INVERSE_OFF+";"+STRIKETHROUGH_OFF
INVERSE_ONLY = BOLD_OFF+";"+ITALICS_OFF+";"+UNDERLINE_OFF+";"+INVERSE+";"+STRIKETHROUGH_OFF
STRIKETHROUGH_ONLY = BOLD_OFF+";"+ITALICS_OFF+";"+UNDERLINE_OFF+";"+INVERSE_OFF+";"+STRIKETHROUGH

BLACK_COLOR = "30"
RED_COLOR = "31"
GREEN_COLOR = "32"
YELLOW_COLOR = "33"
BLUE_COLOR = "34"
MAGENTA_COLOR = "35"
CYAN_COLOR = "36"
WHITE_COLOR = "37"
DEFAULT_COLOR = "39"

BG_BLACK_COLOR = "40"
BG_RED_COLOR = "41"
BG_GREEN_COLOR = "42"
BG_YELLOW_COLOR = "43"
BG_BLUE_COLOR = "44"
BG_MAGENTA_COLOR = "45"
BG_CYAN_COLOR = "46"
BG_WHITE_COLOR = "47"
BG_DEFAULT_COLOR = "49"


# 2 character codes, color and attribute
# e.g. blue bold - bb, blue normal - bn
# z = black, b = blue, xx = reset,
# u=underling, n=normal, b=bold, i=inverse
color_codes = {
    "}}xx": CSI+RESET_COLOR+"m",
    
    "}}zu": CSI+UNDERLINE_ONLY+";"+BLACK_COLOR+";"+BG_WHITE_COLOR+"m",
    "}}ru": CSI+UNDERLINE_ONLY+";"+RED_COLOR+";"+BG_DEFAULT_COLOR+"m",
    "}}gu": CSI+UNDERLINE_ONLY+";"+GREEN_COLOR+";"+BG_DEFAULT_COLOR+"m",
    "}}yu": CSI+UNDERLINE_ONLY+";"+YELLOW_COLOR+";"+BG_DEFAULT_COLOR+"m",
    "}}bu": CSI+UNDERLINE_ONLY+";"+BLUE_COLOR+";"+BG_DEFAULT_COLOR+"m",
    "}}mu": CSI+UNDERLINE_ONLY+";"+MAGENTA_COLOR+";"+BG_DEFAULT_COLOR+"m",
    "}}cu": CSI+UNDERLINE_ONLY+";"+CYAN_COLOR+";"+BG_DEFAULT_COLOR+"m",
    "}}wu": CSI+UNDERLINE_ONLY+";"+WHITE_COLOR+";"+BG_DEFAULT_COLOR+"m",
    "}}du": CSI+UNDERLINE_ONLY+";"+DEFAULT_COLOR+";"+BG_DEFAULT_COLOR+"m",
    
    "}}zi": CSI+INVERSE_ONLY+";"+BOLD_OFF+";"+BLACK_COLOR+";"+BG_WHITE_COLOR+"m",
    "}}ri": CSI+INVERSE_ONLY+";"+RED_COLOR+";"+BG_DEFAULT_COLOR+"m",
    "}}gi": CSI+INVERSE_ONLY+";"+GREEN_COLOR+";"+BG_DEFAULT_COLOR+"m",
    "}}yi": CSI+INVERSE_ONLY+";"+YELLOW_COLOR+";"+BG_DEFAULT_COLOR+"m",
    "}}bi": CSI+INVERSE_ONLY+";"+BLUE_COLOR+";"+BG_DEFAULT_COLOR+"m",
    "}}mi": CSI+INVERSE_ONLY+";"+MAGENTA_COLOR+";"+BG_DEFAULT_COLOR+"m",
    "}}ci": CSI+INVERSE_ONLY+";"+CYAN_COLOR+";"+BG_DEFAULT_COLOR+"m",
    "}}wi": CSI+INVERSE_ONLY+";"+WHITE_COLOR+";"+BG_DEFAULT_COLOR+"m",
    "}}di": CSI+INVERSE_ONLY+";"+DEFAULT_COLOR+";"+BG_DEFAULT_COLOR+"m",
    
    
    "}}zn": CSI+NORMAL_ONLY+";"+BLACK_COLOR+";"+BG_WHITE_COLOR+"m",
    "}}rn": CSI+NORMAL_ONLY+";"+RED_COLOR+";"+BG_DEFAULT_COLOR+"m",
    "}}gn": CSI+NORMAL_ONLY+";"+GREEN_COLOR+";"+BG_DEFAULT_COLOR+"m",
    "}}yn": CSI+NORMAL_ONLY+";"+YELLOW_COLOR+";"+BG_DEFAULT_COLOR+"m",
    "}}bn": CSI+NORMAL_ONLY+";"+BLUE_COLOR+";"+BG_DEFAULT_COLOR+"m",
    "}}mn": CSI+NORMAL_ONLY+";"+MAGENTA_COLOR+";"+BG_DEFAULT_COLOR+"m",
    "}}cn": CSI+NORMAL_ONLY+";"+CYAN_COLOR+";"+BG_DEFAULT_COLOR+"m",
    "}}wn": CSI+NORMAL_ONLY+";"+WHITE_COLOR+";"+BG_DEFAULT_COLOR+"m",
    "}}dn": CSI+NORMAL_ONLY+";"+DEFAULT_COLOR+";"+BG_DEFAULT_COLOR+"m",
    
    "}}zb": CSI+BOLD_ONLY+";"+BLACK_COLOR+";"+BG_WHITE_COLOR+"m",
    "}}rb": CSI+BOLD_ONLY+";"+RED_COLOR+";"+BG_DEFAULT_COLOR+"m",
    "}}gb": CSI+BOLD_ONLY+";"+GREEN_COLOR+";"+BG_DEFAULT_COLOR+"m",
    "}}yb": CSI+BOLD_ONLY+";"+YELLOW_COLOR+";"+BG_DEFAULT_COLOR+"m",
    "}}bb": CSI+BOLD_ONLY+";"+BLUE_COLOR+";"+BG_DEFAULT_COLOR+"m",
    "}}mb": CSI+BOLD_ONLY+";"+MAGENTA_COLOR+";"+BG_DEFAULT_COLOR+"m",
    "}}cb": CSI+BOLD_ONLY+";"+CYAN_COLOR+";"+BG_DEFAULT_COLOR+"m",
    "}}wb": CSI+BOLD_ONLY+";"+WHITE_COLOR+";"+BG_DEFAULT_COLOR+"m",
    "}}db": CSI+BOLD_ONLY+";"+DEFAULT_COLOR+";"+BG_DEFAULT_COLOR+"m",
}


def colorTest():
    ret = ""
    
    for c in color_codes:
        ret += c + c.replace("}}", "") + "\n"
    
    return ret


def translateColorCodes(txt):
    # Find and translate all color codes to ASCII color codes
    for c in color_codes:
        txt = txt.replace(c, color_codes[c])
    
    # Look for position codes
    # {{x,y;
    i = txt.find("{{")
    last = 0
    while i > -1:
        last = i
        # Found an {{, look for the ending ;
        i2 = txt.find(";", i+2)
        if i2 > -1:
            # Extract the position text
            pos_txt = txt[i: i2+1]
            # print "POS TXT" + str(pos_txt) + " " + str(i) + "/" + str(i2)
            # Strip off {{ and ;
            pos_txt2 = pos_txt.replace("{{", "").replace(";", "")
            # Split on ,
            parts = pos_txt2.split(",")
            if len(parts) != 2:
                print("Invalid pos??")
            else:
                # x in 0, y in 1
                x = parts[0]
                y = parts[1]
                # Build up ansi pos string
                ansi_txt = CSI+y+";"+x+"H"
                txt = txt.replace(pos_txt, ansi_txt)
                
        i = txt.find("{{", last+2)
        
    
    return txt


def clearScreen():
    return CLEAR_SCREEN


def setTermPos(x, y, out=sys.stdout):
    out.write(CSI + str(y) + ";" + str(x) + "H")


def p(txt, lf=True):
    txt = translateColorCodes(txt)
    if lf is True:
        print(txt)
    else:
        print(txt, end='')
