# ope
Open Prison Education - A docker based environment to easily install and download online resources for an offline environment

# NOTE - 6/7/17 - BIG CHANGES
Revising to use dockerhub to pull built images as well as include client tools/etc...
This is currently in process and could mean breaking changes to the prev build process.

# Overview
Getting online resources into a facility with limited or non-existant internet access can be difficult. This is an attempt to deal with the infrastructure problems associated with setting up web services and transferring applications and data to an inside server.

# Micro Service Architecture
We utilize Docker containers for micro services. You will need a machine that can run docker containers on the outside to build and setup your services, and a docker machine on the inside to transfer images and data to.

Online Docker Machine --> Portable USB Drive --> Offline Docker Machine

# Getting Started
1) Install Docker on your servers (once on online server, once on offline server). This is a linux image that you can install as a VM or directly on a server: https://susestudio.com/a/P08rUy/ope-docker

2) Ensure adequate storage space - 2 TB recommended storage, 32 gig ram

3) Install python 2.7 on both machines (https://www.python.org/ - choose 2.7? MSI installer for windows, linux should already have it)

4) Clone the ope project to your online server: git clone https://github.com/frankyrumple/ope.git

5) Open a shell and cd to the ope folder (Power shell in windows preferred)

6) Run: python 

7) Run: python rebuild_compose.py - this will build a docker-compose.yml file from the enabled services. If you want to turn off services rename or remove the .enabled file in each folder and run this again.

8) Run: docker-compose build  - this will build the images for each service

9) Run: docker-compose up -d  - This will start all the enabled services.

10) SETUP DNS - For active directory users, add a conditional forwarder for the ed domain to point to the docker machine IP. For linux users, you can add the docker machine ip as a forwarder or setup an ed domain (wildcard?) to point to the docker machine ip.

11) Now you can login to the ones you need to and do any additional setup (e.g. kalite - download kahn videos) - look at http://gateway.ed:8080 to see a list of services available.

12) When done run: docker-compose down  - This shuts down the services

13) Export the images: python export_docker_images.py   - This will create tar files that you can carry in on a portable drive.

14) Sync everything to your portable drive: python sync_to_portable_drive.py  - This will copy the whole ope project folder as well as exported images and volume data to the portable drive. Make sure your drive is big enough to hold it all. We use sync so the first time it will be very slow, but should be much faster the next time.

15) Bring portable drive to offline server. This assumes that your offline server is setup to run docker already.

16) Make sure that you have an OPE folder on your server to transfer stuff to (/ope recommended).

17) From the portable drive, run the sync_from_portable_drive.py script: e.g.   python /mnt/usbdrive/sync_from_portable_drive.py
    When complete, your local ope folder should contain everything from your online computer

18) From the ope folder on the server, run: docker-compose up -d

19) Ensure that DNS is setup on offline network (see step 10)

20) View status at: http://gateway.ed:8080  - check other services. Things should be working.




== DHCP Mods for PXE Boot ==
option space PXE;
option PXE.mtftp-ip    code 1 = ip-address;
option PXE.mtftp-cport code 2 = unsigned integer 16;
option PXE.mtftp-sport code 3 = unsigned integer 16;
option PXE.mtftp-tmout code 4 = unsigned integer 8;
option PXE.mtftp-delay code 5 = unsigned integer 8;
option arch code 93 = unsigned integer 16; # RFC4578
use-host-decl-names on;
ddns-update-style interim;
ignore client-updates;
authoritative;
allow booting;
allow bootp;
option option-128 code 128 = string;
option option-129 code 129 = text;
next-server 192.168.10.203;
#filename "pxelinux.0";
#filename "snponly.efi";
#filename "ipxe.efi";
option tftp-server-name "192.168.10.203";
#option bootfile-name "pelinux.0";
#option bootfile-name "undionly.kpxe";  # works for vmplayer
#option bootfile-name "snponly.efi";
#option bootfile-name "ipxe.efi";
#range dynamic-bootp 192.168.10.25 192.168.10.28;

class "UEFI-32-1" {
    match if substring(option vendor-class-identifier, 0, 20) = "PXEClient:Arch:00006";
    filename "i386-efi/ipxe.efi";
    }

    class "UEFI-32-2" {
    match if substring(option vendor-class-identifier, 0, 20) = "PXEClient:Arch:00002";
     filename "i386-efi/ipxe.efi";
    }

    class "UEFI-64-1" {
    match if substring(option vendor-class-identifier, 0, 20) = "PXEClient:Arch:00007";
     #filename "ipxe.efi";
     filename "snp.efi";
    }

    class "UEFI-64-2" {
    match if substring(option vendor-class-identifier, 0, 20) = "PXEClient:Arch:00008";
    #filename "ipxe.efi";
     filename "snp.efi";
    }

    class "UEFI-64-3" {
    match if substring(option vendor-class-identifier, 0, 20) = "PXEClient:Arch:00009";
     #filename "ipxe.efi";
     filename "snp.efi";
    }

    class "Legacy" {
    match if substring(option vendor-class-identifier, 0, 20) = "PXEClient:Arch:00000";
    filename "undionly.kkpxe";
    }