# from win32com.shell import shell, shellcon
import os
import sys
import time
import pyscreenshot as ImageGrab
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import logging
import ntsecuritycon
import win32security
import win32api
import win32gui
import win32ui
import win32con
import getpass
import datetime
import ctypes

# ROOT_FOLDER = os.path.join(shell.SHGetFolderPath(0, shellcon.CSIDL_COMMON_APPDATA, None, 0), "ope")
ROOT_FOLDER = "c:\\programdata\\ope"
LOG_FOLDER = os.path.join(ROOT_FOLDER, "tmp\\log")
SCREEN_SHOTS_FOLDER = os.path.join(ROOT_FOLDER, "tmp\\screen_shots")
PIC_TYPE = ".png"

# Make sure folder exists
if not os.path.isdir(SCREEN_SHOTS_FOLDER):
    os.makedirs(SCREEN_SHOTS_FOLDER)
if not os.path.isdir(LOG_FOLDER):
    os.makedirs(LOG_FOLDER)

logging.basicConfig(
    filename=os.path.join(LOG_FOLDER, 'ope-sshot.log'),
    level=logging.DEBUG,
    datefmt='%Y-%m-%d %H:%M:%S',
    format='[ope-sshot] %(asctime)-15s %(levelname)-7.7s %(message)s'
)


def grab_screen_area(x1, y1, x2, y2):
    # NOTE - Not used - early example
    # Grab part of the screen
    im = ImageGrab.grab(bbox=(x1, y1, x2, y2))

    # Save the file
    im.save(os.path.join(SCREEN_SHOTS_FOLDER, str(time.time()) + PIC_TYPE), optimize=True)

    # Show image in a window
    # im.show()


def grab_full_screen():
    # NOTE - Not used - early example
    # Grab the screen
    im = ImageGrab.grab()

    # Size it down
    # im.thumbnail((512, 512))
    size_multiplier = .5
    w = int(im.size[0] * size_multiplier)
    h = int(im.size[1] * size_multiplier)
    im = im.resize((w, h), Image.ANTIALIAS)
    im = im.convert('P', palette=Image.ADAPTIVE, colors=256)

    # Save the file
    im.save(os.path.join(SCREEN_SHOTS_FOLDER, str(time.time()) + PIC_TYPE), optimize=True)

    # Show image in a window
    # im.show()


def grabScreenShot():
    # Grab the screen shot and save it to the logs folder
    # Get the hwnd for the current desktop window
    try:
        # Deal with DPI Differences - can cause sshot to be cut off
        ctypes.windll.user32.SetProcessDPIAware()

        hwnd = win32gui.GetDesktopWindow()
        # hwnd = self.getDesktopHWND()
        # NOTE - adjusted to grab whole virtual screen, not just single desktop
        # l, t, r, b = win32gui.GetWindowRect(hwnd)
        # w = r - l
        # h = b - t

        # Get full virtual screen dimensions (all monitors)
        l = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
        t = win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)
        w = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
        h = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)
        r = l + w
        b = t + h

        # logging.info("SC - HWND " + str(hwnd) + " " + str(w) + "/" + str(h))
        
        dc = win32gui.GetDC(hwnd)  # win32con.HWND_DESKTOP)
        # logging.info("DC " + str(dc))
        
        dcObj = win32ui.CreateDCFromHandle(dc)
        drawDC = dcObj.CreateCompatibleDC()
        # logging.info("drawDC " + str(drawDC))
        
        # cDC = dcObj.CreateCompatibleDC() # Do we need this since it is the desktop dc?
        bm = win32ui.CreateBitmap()
        bm.CreateCompatibleBitmap(dcObj, w, h)
        drawDC.SelectObject(bm)
        # drawDC.BitBlt((0, 0), (w, h), dcObj, (0, 0), win32con.SRCCOPY)
        drawDC.BitBlt((0, 0), (w, h), dcObj, (l, t), win32con.SRCCOPY)

        sshot_time = str(time.time())
        f_path = os.path.join(SCREEN_SHOTS_FOLDER, sshot_time + PIC_TYPE)
        logging.info("Saving sshot " + f_path)

        # Convert to an image and save
        # bm.SaveBitmapFile(drawDC, f_path)
        bmInfo = bm.GetInfo()
        bmBits = bm.GetBitmapBits(True)
        sshot_img = Image.frombuffer('RGB', (bmInfo['bmWidth'], bmInfo['bmHeight']),
            bmBits, 'raw', 'BGRX', 0, 1)
        
        size_multiplier = .5
        w = int(sshot_img.size[0] * size_multiplier)
        h = int(sshot_img.size[1] * size_multiplier)
        sshot_img = sshot_img.resize((w, h), Image.ANTIALIAS)
        # sshot_img = sshot_img.convert('P', palette=Image.ADAPTIVE, colors=256)

        # Build overlay graphic w user/time banner
        # Ends up w computer name when run from service?
        #curr_user = getpass.getuser()
        curr_user = win32api.GetUserName()
        banner_height = 40
        banner_width = sshot_img.width
        banner_img = Image.new('RGBA', (banner_width, banner_height), 'black')
        draw = ImageDraw.Draw(banner_img)
        # Draw Rectangle
        # draw.rectangle((0, bmInfo['bmHeight'], 100, 30), outline='blue', fill='white')
        font = ImageFont.truetype("STENCIL.ttf", 16)
        draw.text((5, 5), "Current User: " + str(curr_user), (255, 255, 255), font=font)
        draw.text((5, 20), str(datetime.datetime.now()), (255, 255, 255), font=font)
        draw.text((300, 5), "Time Stamp: " + sshot_time, (255, 255, 255), font=font)

        # Build a new image big enough for both
        final_img = Image.new("RGBA", (sshot_img.width, sshot_img.height + banner_height), 'black')
        # Put in the sshot in the final image
        final_img.paste(sshot_img, (0, 0))
        # Put the banner in the final image
        final_img.paste(banner_img, (0, sshot_img.height))

        # Convert to fewer colors
        final_img = final_img.convert('P', palette=Image.ADAPTIVE, colors=256)

        # Save the file
        final_img.save(f_path, optimize=True)
            
        win32gui.DeleteObject(bm.GetHandle())
        drawDC.DeleteDC()
        dcObj.DeleteDC()
        win32gui.ReleaseDC(win32con.HWND_DESKTOP, dc)
        
        # dc = win32gui.GetWindowDC(hwnd)
        # logging.info("DC " + str(dc))
        # dcObj = win32ui.CreateDCFromHandle(dc)
        # logging.info("dcObj " + str(dcObj))
        # cDC = dcObj.CreateCompatibleDC()
        # logging.info("cDC " + str(cDC))
        # bm = win32ui.CreateBitmap()
        # logging.info("bm " + str(bm))
        # bm.CreateCompatibleBitmap(dcObj, w, h)
        # cDC.SelectObject(bm)
        # r = cDC.BitBlt((0,0), (w,h), dcObj, (0,0), win32con.SRCCOPY)
        # logging.info("bitblt " + str(r))
        # bm.SaveBitmapFile(cDC, os.path.join(SCREEN_SHOTS_FOLDER, "test.jpeg"))
        # dcObj.DeleteDC()
        # cDC.DeleteDC()
        # win32gui.ReleaseDC(hwnd, dc)
        # win32gui.DeleteObject(bm.GetHandle())
    except Exception as ex:
        logging.info("Error grabbing screen shot: " + str(ex))
    
    # m = ImageGrab.grab()

    # Save the file
    # p = os.path.join(SCREEN_SHOTS_FOLDER, str(datetime.datetime.now()) + ".png")
    # im.save(p, optimize=True)


if __name__ == '__main__':
    # freeze_support()
    # grab_full_screen()
    # grab_screen_area(10, 10, 510, 510)
    print("Grabbing screen shot...")
    # logging.info("SShot called...")
    grabScreenShot()
