# OPE - Client Tools


These tools are for the client computers (Laptops). They help with things like security settings, monitoring, syncing, etc...


## lms
- The LMS app which sync with Canvas. This is the primary delivery point for curriculum to students. It talks directly with Canvas to pull materials and translate materials to run local. This includes pulling videos/documents from the SMC


## svc
OPE Service - monitors security, does auto upgrades, takes screen shots, etc... Primary tool to keep things locked down

## bin
Apps (like wget.exe) and scripts that are used by the system to do various things like set security options, import/export group policy, etc... Release versions of stuff are in the ope_laptop_binaries repo.


## Major Changes
- 4/1/20 - sshot utility combined into the svc folder - setup to build both as well as other utilities in the same location
- 4/1/20 - Convert sshot and ope service to python3
