@echo off

netsh advfirewall import "%~dp0rc\firewall_config.wfw" 2>NUL 1<NUL
