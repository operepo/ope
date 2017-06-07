

# Antivirus scan


def download_current_av():
    # Download the current AV files from server (should auto pull from clamav.ed)
    cmd = "freshclam.exe"

    pass

def scan_folders():
    # Start scanning folders with the AV scanner

    folder_list = []
    for folder in folder_list:
        cmd = "clamscan -r -i {0}".format(folder)

    pass



if __name__ == "__main__":
    # Scan some stuff... TODO
    pass
