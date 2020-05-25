@echo off

netsh advfirewall export "%~dp0rc\firewall_config.wfw"