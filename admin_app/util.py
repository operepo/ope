import sys
import os
import re
from os.path import expanduser

global APP_FOLDER
APP_FOLDER = None


def get_human_file_size(size):
    sizes = ["B", "K", "M", "G", "T"]
    count = 0
    t = size
    while t > 1024:
        t /= 1024
        count += 1

    ret = "{0:.2f}".format(t) + " " + sizes[count]
    return ret


def get_home_folder():
    home_path = expanduser("~")
    return home_path

def get_app_folder():
    global Logger, APP_FOLDER
    ret = ""
    # Adjusted to save APP_FOLDER - issue #6 - app_folder not returning the same folder later in the app?
    if APP_FOLDER is None:
        # return the folder this app is running in.
        # Logger.info("Application: get_app_folder called...")
        if getattr(sys, 'frozen', False):
            # Running in pyinstaller bundle
            ret = sys._MEIPASS
            # Logger.info("Application: sys._MEIPASS " + sys._MEIPASS)
            # Adjust to use sys.executable to deal with issue #6 - path different if cwd done
            # ret = os.path.dirname(sys.executable)
            # Logger.info("AppPath: sys.executable " + ret)

        else:
            ret = os.path.dirname(os.path.abspath(__file__))
            # Logger.info("AppPath: __file__ " + ret)
        APP_FOLDER = ret
        # Add this folder to the os path so that resources can be found more reliably
        text_dir = os.path.join(APP_FOLDER, "kivy\\core\\text")
        os.environ["PATH"] = os.environ["PATH"] + ";" + ret + ";" + text_dir
        print("-- ADJUSTING SYS PATH -- " + os.environ["PATH"])

    else:
        ret = APP_FOLDER
    return ret




# <editor-fold desc="Markdown Functions">
# Convert markdown code to bbcode tags so they draw properly in labels
def markdown_to_bbcode(s):
    links = {}
    codes = []

    def gather_link(m):
        links[m.group(1)]=m.group(2); return ""

    def replace_link(m):
        return "[url=%s]%s[/url]" % (links[m.group(2) or m.group(1)], m.group(1))

    def gather_code(m):
        codes.append(m.group(3)); return "[code=%d]" % len(codes)

    def replace_code(m):
        return "%s" % codes[int(m.group(1)) - 1]

    def translate(p="%s", g=1):
        def inline(m):
            s = m.group(g)
            s = re.sub(r"(`+)(\s*)(.*?)\2\1", gather_code, s)
            s = re.sub(r"\[(.*?)\]\[(.*?)\]", replace_link, s)
            s = re.sub(r"\[(.*?)\]\((.*?)\)", "[url=\\2]\\1[/url]", s)
            s = re.sub(r"<(https?:\S+)>", "[url=\\1]\\1[/url]", s)
            s = re.sub(r"\B([*_]{2})\b(.+?)\1\B", "[b]\\2[/b]", s)
            s = re.sub(r"\B([*_])\b(.+?)\1\B", "[i]\\2[/i]", s)
            return p % s
        return inline

    s = re.sub(r"(?m)^\[(.*?)]:\s*(\S+).*$", gather_link, s)
    s = re.sub(r"(?m)^    (.*)$", "~[code]\\1[/code]", s)
    s = re.sub(r"(?m)^(\S.*)\n=+\s*$", translate("~[size=24][b]%s[/b][/size]"), s)
    s = re.sub(r"(?m)^(\S.*)\n-+\s*$", translate("~[size=18][b]%s[/b][/size]"), s)
    s = re.sub(r"(?m)^#\s+(.*?)\s*#*$", translate("~[size=24][b]%s[/b][/size]"), s)
    s = re.sub(r"(?m)^##\s+(.*?)\s*#*$", translate("~[size=18][b]%s[/b][/size]"), s)
    s = re.sub(r"(?m)^###\s+(.*?)\s*#*$", translate("~[b]%s[/b]"), s)
    s = re.sub(r"(?m)^####\s+(.*?)\s*#*$", translate("~[b]%s[/b]"), s)
    s = re.sub(r"(?m)^> (.*)$", translate("~[quote]%s[/quote]"), s)
    # s = re.sub(r"(?m)^[-+*]\s+(.*)$", translate("~[list]\n[*]%s\n[/list]"), s)
    # s = re.sub(r"(?m)^\d+\.\s+(.*)$", translate("~[list=1]\n[*]%s\n[/list]"), s)
    s = re.sub(r"(?m)^((?!~).*)$", translate(), s)
    s = re.sub(r"(?m)^~\[", "[", s)
    s = re.sub(r"\[/code]\n\[code(=.*?)?]", "\n", s)
    s = re.sub(r"\[/quote]\n\[quote]", "\n", s)
    s = re.sub(r"\[/list]\n\[list(=1)?]\n", "", s)
    s = re.sub(r"(?m)\[code=(\d+)]", replace_code, s)

    return s
# </editor-fold>