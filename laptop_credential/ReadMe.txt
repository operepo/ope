## RUN AS PYTHON 2.x if not compiled

# Laptop Credential Application

## What is it?
To setup a secured laptop that is properly configured to sync with Canvas, this app will
do the job of installing services and applying settings that are needed.


## Credential Steps

- Contact SMC for Canvas Auth Token
- Create a local windows user
- Create a local OPEStudents group and add the user to it
- Store Auth token in the registry where the student account can access it
- Install the OPE Laptop Admin service on the machine
- Apply list of group policy settings locally
- Install anti virus software

- Randomize Admin account password - in case it gets


##
NOTE - Modified winsys to allow 32/64 bit registry views
