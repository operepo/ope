
# OPE Project - Release Notes
Important notifications and heads up on what has changed.

## [color=ff3333]!!!SECURITY ADVISORY - 5/1/2020 !!![/color]
Please make sure that laptops are all re-credentialed with the latest updates. Credential app now shows a version nubmer in green and needs to be v1.0.24 or higher. This is an urgent update and requires that all laptops be pulled ASAP and re-credentialed.

## [color=ff3333]!!!PASSWORD WARNING!!![/color]
Short passwords no longer work! Please make sure you use proper password complexity (8 characters, 1 capital, 1 lower case, 1 number, 1 symbol) for admin/facuty/student accounts as weak passwords will be rejected. Short passwords have been known to cause the following problems:
- User accounts NOT showing up in canvas after SMC import
- Canvas not properly starting up with admin/root password too short

## [color=33ff33]CURRENT VERSIONS - Updated 5/8/2020[/color]
- SyncApp 1.33
- Laptop Credential 1.0.24
- SMC 1.9.41

## (NOT RELEASED YET)
- LMS App
  * Auto accept courses in Canvas during sync
  * Show courses that aren't published during sync
  * Better formatting/errors during sync
  * mgmt tool - allows greater control over settings
  * Auto Update - laptops now auto update and re-apply security settings without staff intervention

- SMC
  * Ability to prevent change password tools for students/faculty in SMC
  * Fixes for finding username - existing users should still work after changing username pattern
  * Added laptop logging rights on faculty management screen - allow staff to view laptop logs

## 6/1/2020
- Sync App
  * Add ope-ntp app - allow server to respond to time requests as well as sync from time.windows.com (or other specified source)

## 5/8/2020
- SyncApp 1.32
  * Fixes to local id_rsa cert on new computers, also caused issues with known_hosts and unknown certs errors
  * Added SUCCESS/FAILED message on multiple locations to show when git or docker commands fail more clearly

## 5/4/2020
- SyncApp 1.31
  * Fix known_hosts error - when running and known_hosts file doesn't already exist.


## 4/13/2020
- SMC 
  * Version 1.9.40
- SyncApp
  * Starting release notes
  * added rce and manthan options to pick apps
- Canvas
  * updated with mathman extension (for equation rendering)
- SMC
  * upated from python2 to python3
  * SMC - Added ability to edit media descriptions/information

