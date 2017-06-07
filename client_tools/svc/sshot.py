
# pip install pillow
# pip install pyscreenshot


import pyscreenshot as ImageGrab

def grab_screen_area(x1, y1, x2, y2):
    # Grab part of the screen
    im = ImageGrab.grab(bbox=(x1, y1, x2, y2))

    # Save the file
    im.save("sshot_part.png")

    # Show image in a window
    # im.show()

def grab_full_screen():
    # Grab the screen
    im = ImageGrab.grab()

    # Save the file
    im.save("sshot.png")

    # Show image in a window
    # im.show()

if __name__ == '__main__':
    # freeze_support()

    grab_full_screen()
    grab_screen_area(10, 10, 510, 510)
