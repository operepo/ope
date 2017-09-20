
# Getting Started - OPE System

## Purpose:
To allow easy access to educational resources to inmates who have no internet connectivity.on_press

## System Components:
The main OPE components includes the following parts:
- Server Components - Docker containers that run server apps such as Canvas that can be used on your local network
- Docking Station - A device that inmate laptops can plug into and sync with Canvas
- Inmate Laptops - A laptop device that meets DOC security requirements

# Server Components

## Initial Setup
To begin using the OPE server components, you will need to setup your servers on a computer outside the DOC facility
with internet access.

We recommend a desktop or laptop on campus that has at 8 gig of ram and a terabyte or more of hard disk space.

### Install with VirutalBox - Recommended
The recommended method of setup is to install the OPE system on a windows machine using VirtualBox. This is the easiest
method and requires the least knowledge of Linux or other system tools.

#### Download VirtualBox

https://www.virtualbox.org/wiki/Downloads
- Download the link that says "Windows Hosts"
- Download the Extension Pack - "All Supported Platforms"
- Install VirtualBox
- Double click extension pack after installing VirtualBox and follow instructions

#### Download OPE binary file (OVR Package)
We have a pre-made package that has the parts already installed that you will need. All you need to do is set the
password and IP address for your network.

TODO - LINK

This package contains:
- OpenSuse Linux with Docker and other packages installed
- IPTables rules to properly pass through NAT/TFTP/NFS and other needed protocols
