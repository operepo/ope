
# Getting Started - OPE System

## Purpose:
To allow easy deployment of educational resources to inmates who have no internet connectivity. This includes deployment of servers (canvas, smc, gcflearnfree, etc...), tools to help with offline conversion (smc video tools to replace youtube and find/replace for converting curriculum), and last mile delivery on laptop systems that can work fully offline and sync with the education server.

## System Components:
The main OPE components includes the following parts:
- Server Components - Docker containers that run server apps such as Canvas that are prison ready and can be used on your local network
- Docking Station - A device that inmate laptops can plug into and sync with Canvas (custom sync box, or newer style dock on 2nd generation laptops)
- Inmate Laptops - A laptop device that meets DOC security requirements

## Further Documentation
Documentation and videos showing how to setup and use the system are located at:
https://github.com/operepo/ope_documentation
and
https://github.com/operepo/ope_vids

The main github repository is at:
https://github.com/operepo

[b]These are the repos you will want to check out:[/b]
- ope_vids - Screen cast instructional videos showing the full setup process
- ope_documentation - Written documentation
- ope_server_sync_binaries - The admin app and stuff it needs to run. This is the one you download to get this app and get started

[b]Optional Repos for developers - Check these out if you are a developer or want to dig deeper into the system:[/b]
- ope - The source code for most of the project - use this if you want to write code and help modify the project
- smc - The source code for the SMC server
- ope_laptop_binaries - The built copies of software that runs on the laptop when credentialed - automatically pulled in during sync/credential - all source is in the ope repo
- wsl_wiki - Source code for the WA State Library Re-Entry wiki - Use to build a copy of the wiki that the WA State Library has compiled containing numerous re-entry resources
- sysprep_scripts - Scripts used to ready a windows 10 desktop ready for sysprep as well as post setup scripts that activate win/office and fog service (auto join active directory)

