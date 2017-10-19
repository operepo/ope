from win32com.shell import shell, shellcon
import os
import sys
import time
from PIL import Image
import pyscreenshot as ImageGrab

LOG_FOLDER = os.path.join(shell.SHGetFolderPath(0, shellcon.CSIDL_COMMON_APPDATA, None, 0), "ope")
SCREEN_SHOTS_FOLDER = os.path.join(LOG_FOLDER, "screen_shots")
PIC_TYPE = ".png"

def grab_screen_area(x1, y1, x2, y2):
    # Grab part of the screen
    im = ImageGrab.grab(bbox=(x1, y1, x2, y2))

    # Save the file
    im.save(os.path.join(SCREEN_SHOTS_FOLDER, str(time.time()) + PIC_TYPE), optimize=True)

    # Show image in a window
    # im.show()

def grab_full_screen():
    # Grab the screen
    im = ImageGrab.grab()

    # Size it down
    #im.thumbnail((512, 512))
    size_multiplier = .5
    w = int(im.size[0] * size_multiplier)
    h = int(im.size[1] * size_multiplier)
    im = im.resize((w, h), Image.ANTIALIAS)
    im = im.convert('P', palette=Image.ADAPTIVE, colors=256)

    # Save the file
    im.save(os.path.join(SCREEN_SHOTS_FOLDER, str(time.time()) + PIC_TYPE), optimize=True)

    # Show image in a window
    # im.show()

if __name__ == '__main__':
    # freeze_support()
    grab_full_screen()
    # grab_screen_area(10, 10, 510, 510)
