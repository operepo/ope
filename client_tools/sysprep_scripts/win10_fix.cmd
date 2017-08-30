@echo off

rem fix issues w win 10
Dism /Online /Cleanup-Image /RestoreHealth
Dism.exe /online /Cleanup-Image /StartComponentCleanup
sfc /scannow

rem (poewrshell) Disable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V-All
rem dism.exe /Online /Enable-Feature:Microsoft-Hyper-V /All
rem dism.exe /Online /Disable-Feature:Microsoft-Hyper-V

rem verbose shutdown
rem reg ADD "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" /v VerboseStatus /t REG_DWORD /d 1 /f

rem Don't clear page file at shutdown - faster shutdown
rem reg ADD "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management" /v ClearPageFileAtShutdown /t REG_DWORD /d 0 /f

rem  to put apps back:
rem Add-AppxPackage -register "C:\Program Files\WindowsApps\Microsoft.DesktopAppInstaller_1.0.10332.0_x64__8wekyb3d8bbwe\appxmanifest.xml" -DisableDevelopmentMode

chkdsk /f c:
rem defrag c:
