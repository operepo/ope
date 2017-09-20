
# Install
Copy the scripts to c:\apps\sysprep_scripts

# 2 Steps
The script is split so that less common things that happen only once are in the first step (e.g. remove apps)

Things that you do every time you boot up and modify the image are in step 2

You should only need to run step2 when updating the image in the future.

# Run
Run a command prompt as admin (NOT POWERSHELL)

CD to the folder (cd c:\apps\sysprep_scripts)
run step1 (step1.cmd)
It should reboot
run step2 (step2.cmd)
It should shutdown

Start capture task while the machine is shutdown.
( NOTE - don't use resize partition for best results )

Power on the machine and it should start capturing the image.



# Helpful Resources

Online windows answer file generator (also other great tools)
http://windowsafg.no-ip.org/index.html

Chrome Enterprise
https://enterprise.google.com/chrome/chrome-browser/#