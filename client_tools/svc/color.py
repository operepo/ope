import sys
from colorama import init  # , Fore, Back, Style
# strip=False - so that colors work in pycharm console
init(strip=False)

DEBUG_LEVEL = 0

CSI = "\x1b["
CLEAR_SCREEN = CSI + "2J"
RESET_COLOR = CSI + "0m"

BOLD = "1"
ITALICS = "3"
UNDERLINE = "4"
INVERSE = "7"
STRIKE_THROUGH = "9"

BOLD_OFF = "22"
ITALICS_OFF = "23"
UNDERLINE_OFF = "24"
INVERSE_OFF = "27"
STRIKE_THROUGH_OFF = "29"

NORMAL_ONLY = BOLD_OFF + ";" + ITALICS_OFF + ";" + UNDERLINE_OFF + ";" + \
            INVERSE_OFF + ";" + STRIKE_THROUGH_OFF + ";"
BOLD_ONLY = BOLD + ";" + ITALICS_OFF + ";" + UNDERLINE_OFF + ";" + \
            INVERSE_OFF + ";" + STRIKE_THROUGH_OFF + ";"
ITALICS_ONLY = BOLD_OFF + ";" + ITALICS + ";" + UNDERLINE_OFF + ";" + \
            INVERSE_OFF + ";" + STRIKE_THROUGH_OFF + ";"
UNDERLINE_ONLY = BOLD_OFF + ";" + ITALICS_OFF + ";" + UNDERLINE + ";" + \
            INVERSE_OFF + ";" + STRIKE_THROUGH_OFF + ";"
INVERSE_ONLY = BOLD_OFF + ";" + ITALICS_OFF + ";" + UNDERLINE_OFF + ";" + \
            INVERSE + ";" + STRIKE_THROUGH_OFF + ";"
STRIKE_THROUGH_ONLY = BOLD_OFF + ";" + ITALICS_OFF + ";" + UNDERLINE_OFF + \
            ";" + INVERSE_OFF + ";" + STRIKE_THROUGH + ";"


BLACK_COLOR = "30;41m"
Z_COLOR = "30m"
RED_COLOR = "31;49m"
R_COLOR = "31m"
GREEN_COLOR = "32;49m"
G_COLOR = "32m"
YELLOW_COLOR = "33;49m"
Y_COLOR = "33m"
BLUE_COLOR = "34;49m"
B_COLOR = "34m"
MAGENTA_COLOR = "35;49m"
M_COLOR = "35m"
CYAN_COLOR = "36;49m"
C_COLOR = "36m"
WHITE_COLOR = "37;49m"
W_COLOR = "37m"

ALT_C_COLOR = "0;36;1m"

color_codes = {

    "}}xx": RESET_COLOR,

    "}}ac": CSI + ALT_C_COLOR,

    "}}zd": CSI + Z_COLOR,
    "}}rd": CSI + R_COLOR,
    "}}gd": CSI + G_COLOR,
    "}}yd": CSI + Y_COLOR,
    "}}bd": CSI + B_COLOR,
    "}}md": CSI + M_COLOR,
    "}}cd": CSI + C_COLOR,
    "}}wd": CSI + W_COLOR,

    "}}zn": CSI + NORMAL_ONLY + BLACK_COLOR,
    "}}rn": CSI + NORMAL_ONLY + RED_COLOR,
    "}}gn": CSI + NORMAL_ONLY + GREEN_COLOR,
    "}}yn": CSI + NORMAL_ONLY + YELLOW_COLOR,
    "}}bn": CSI + NORMAL_ONLY + BLUE_COLOR,
    "}}mn": CSI + NORMAL_ONLY + MAGENTA_COLOR,
    "}}cn": CSI + NORMAL_ONLY + CYAN_COLOR,
    "}}wn": CSI + NORMAL_ONLY + WHITE_COLOR,

    "}}zb": CSI + BOLD_ONLY + BLACK_COLOR,
    "}}rb": CSI + BOLD_ONLY + RED_COLOR,
    "}}gb": CSI + BOLD_ONLY + GREEN_COLOR,
    "}}yb": CSI + BOLD_ONLY + YELLOW_COLOR,
    "}}bb": CSI + BOLD_ONLY + BLUE_COLOR,
    "}}mb": CSI + BOLD_ONLY + MAGENTA_COLOR,
    "}}cb": CSI + BOLD_ONLY + CYAN_COLOR,
    "}}wb": CSI + BOLD_ONLY + WHITE_COLOR,

    "}}zi": CSI + INVERSE_ONLY + BLACK_COLOR,
    "}}ri": CSI + INVERSE_ONLY + RED_COLOR,
    "}}gi": CSI + INVERSE_ONLY + GREEN_COLOR,
    "}}yi": CSI + INVERSE_ONLY + YELLOW_COLOR,
    "}}bi": CSI + INVERSE_ONLY + BLUE_COLOR,
    "}}mi": CSI + INVERSE_ONLY + MAGENTA_COLOR,
    "}}ci": CSI + INVERSE_ONLY + CYAN_COLOR,
    "}}wi": CSI + INVERSE_ONLY + WHITE_COLOR,

    "}}zu": CSI + UNDERLINE_ONLY + BLACK_COLOR,
    "}}ru": CSI + UNDERLINE_ONLY + RED_COLOR,
    "}}gu": CSI + UNDERLINE_ONLY + GREEN_COLOR,
    "}}yu": CSI + UNDERLINE_ONLY + YELLOW_COLOR,
    "}}bu": CSI + UNDERLINE_ONLY + BLUE_COLOR,
    "}}mu": CSI + UNDERLINE_ONLY + MAGENTA_COLOR,
    "}}cu": CSI + UNDERLINE_ONLY + CYAN_COLOR,
    "}}wu": CSI + UNDERLINE_ONLY + WHITE_COLOR,

}

markup_color_codes = {

    "}}xx": "[/color]",

    "}}ac": "[color=55ffff]",

    "}}zd": "[color=000000]",
    "}}rd": "[color=bb0000]",
    "}}gd": "[color=00bb00]",
    "}}yd": "[color=bbbb00]",
    "}}bd": "[color=0000bb]",
    "}}md": "[color=bb00bb]",
    "}}cd": "[color=00bbbb]",
    "}}wd": "[color=bbbbbb]",

    "}}zn": "[color=000000]",
    "}}rn": "[color=bb0000]",
    "}}gn": "[color=00bb00]",
    "}}yn": "[color=bbbb00]",
    "}}bn": "[color=0000bb]",
    "}}mn": "[color=bb00bb]",
    "}}cn": "[color=00bbbb]",
    "}}wn": "[color=bbbbbb]",

    "}}zb": "[color=555555]",
    "}}rb": "[color=ff5555]",
    "}}gb": "[color=55ff55]",
    "}}yb": "[color=ffff55]",
    "}}bb": "[color=5555ff]",
    "}}mb": "[color=ff55ff]",
    "}}cb": "[color=55ffff]",
    "}}wb": "[color=ffffff]",

    "}}zi": "[color=000000]",
    "}}ri": "[color=bb0000]",
    "}}gi": "[color=00bb00]",
    "}}yi": "[color=bbbb00]",
    "}}bi": "[color=0000bb]",
    "}}mi": "[color=bb00bb]",
    "}}ci": "[color=00bbbb]",
    "}}wi": "[color=bbbbbb]",

    "}}zu": "[color=000000]",
    "}}ru": "[color=bb0000]",
    "}}gu": "[color=00bb00]",
    "}}yu": "[color=bbbb00]",
    "}}bu": "[color=0000bb]",
    "}}mu": "[color=bb00bb]",
    "}}cu": "[color=00bbbb]",
    "}}wu": "[color=bbbbbb]",

}


def set_term_pos(x, y, out=sys.stdout):
    out.write(CSI + str(y) + ";" + str(x) + "H")


def tr(txt):
    return translate_color_codes(txt)

def strip_color_codes(txt):
    global color_codes

    for c in color_codes:
        # Replace with nothing
        txt = txt.replace(c, "")
    
    # Replace position codes
    # {{10,2;
    i = txt.find("{{")
    while i > -1:
        isemi = txt.find(";", i+2)
        if isemi > -1:
            pos_txt = txt[i: isemi+1]
            t = pos_txt.replace("{{", "").replace(";", "")
            parts = t.split(",")
            if len(parts) == 2:
                x = parts[0]
                y = parts[1]
                # Replace with nothing
                #ansi_txt = CSI + y + ";" + x + "H"
                ansi_txt = ""
                txt = txt.replace(pos_txt, ansi_txt)

        i = txt.find("{{", i+1)

    return txt

def translate_color_codes(txt):
    global color_codes

    for c in color_codes:
        txt = txt.replace(c, color_codes[c])

    # {{10,2;
    i = txt.find("{{")
    while i > -1:
        isemi = txt.find(";", i+2)
        if isemi > -1:
            pos_txt = txt[i: isemi+1]
            t = pos_txt.replace("{{", "").replace(";", "")
            parts = t.split(",")
            if len(parts) == 2:
                x = parts[0]
                y = parts[1]
                ansi_txt = CSI + y + ";" + x + "H"
                txt = txt.replace(pos_txt, ansi_txt)

        i = txt.find("{{", i+1)

    return txt


def translate_color_codes_to_markup(txt):
    global color_codes

    # Convert ansi style codes
    for c in color_codes:
        val = color_codes[c]
        txt = txt.replace(val, c)

    # Convert }} type codes
    for c in color_codes:
        txt = txt.replace(c, markup_color_codes[c])

    # # {{10,2;
    # i = txt.find("{{")
    # while i > -1:
    #     isemi = txt.find(";", i+2)
    #     if isemi > -1:
    #         pos_txt = txt[i: isemi+1]
    #         t = pos_txt.replace("{{", "").replace(";", "")
    #         parts = t.split(",")
    #         if len(parts) == 2:
    #             x = parts[0]
    #             y = parts[1]
    #             ansi_txt = CSI + y + ";" + x + "H"
    #             txt = txt.replace(pos_txt, ansi_txt)
    #
    #     i = txt.find("{{", i+1)

    return txt


def p(txt="", end=True, out=None, debug_level=0):
    # Print using the translate colors code

    global DEBUG_LEVEL
    if debug_level > DEBUG_LEVEL:
        # Skip printing anything that is a higher level then our current debug setting
        return

    if out is None:
        out = sys.stdout

    txt = translate_color_codes(txt)
    # Add a line feed when appropriate
    if end is True:
        txt += "\r\n"
    out.write(txt)
    
    out.flush()


if __name__ == "__main__":
    # Print out test stuff
    for c in color_codes:
        p(c.replace("}}", "") + ": " + c + "Testing...}}xx")
