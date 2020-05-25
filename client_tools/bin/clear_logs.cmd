@echo off

set logs_cleared=false

(for /F "usebackq tokens=1*" %%A in (`reg query "HKLM\Software\OPE\OPELMS\LOGS_CLEARED" /ve /reg:64 2^>nul ^| find "REG_" `) DO (
    echo Found Value %%A
    echo :: Logs have been cleared!
    set logs_cleared=true

))

if "%logs_cleared%"=="true" (
    echo Do you want to clear the windows logs again [ default n in 6 seconds ]?
    echo This is not advised after the initial credential process
    choice /C yn /T 6 /D n /M "Press y for yes, or n to skip"
    if errorlevel 2 goto skipclearlogs
)

echo -- Clearing System Logs --



set debug_script=true

(for /F "tokens=*" %%G in ('wevtutil.exe el') DO (
    rem echo clearing log %%G
    if "%debug_script%"=="false" (
        rem wevtutil.exe cl %%G
        echo .
    )
))
rem TODO - clear registry entries at HKLM\System\CurrentControlSet\Enum\USB and
rem HKLM\System\CurrentControlSet\Enum\USBSTORE

rem remove usbstore devices
if "%debug_script%"=="false" (
    echo Debug set
    rem reg delete "HKLM\System\CurrentControlSet\Enum\USBSTORE" /f
)

REM List of devices and their class GUID 
rem https://docs.microsoft.com/en-us/windows-hardware/drivers/install/system-defined-device-setup-classes-available-to-vendors
set approved_devices={36fc9e60-c465-11cf-8056-444553540000}
set bad_devices={53D29EF7-377C-4D14-864B-EB3A85769359} {e0cbf06c-cd8b-4647-bb8a-263b43f0f974} {4d36e965-e325-11ce-bfc1-08002be10318} {4d36e967-e325-11ce-bfc1-08002be10318} {4d36e980-e325-11ce-bfc1-08002be10318} {6bdd1fc3-810f-11d0-bec7-08002be2092f} {4d36e96a-e325-11ce-bfc1-08002be10318} {48721b56-6795-11d2-b1a8-0080c72e74a2} {49ce6ac8-6f86-11d2-b1e5-0080c72e74a2} {7ebefbc0-3200-11d2-b4c2-00a0C9697d07} {6bdd1fc6-810f-11d0-bec7-08002be2092f} {6bdd1fc5-810f-11d0-bec7-08002be2092f} {4d36e96d-e325-11ce-bfc1-08002be10318} {4d36e971-e325-11ce-bfc1-08002be10318} {4d36e96c-e325-11ce-bfc1-08002be10318} {4d36e972-e325-11ce-bfc1-08002be10318} {4d36e979-e325-11ce-bfc1-08002be10318} {4658ee7e-f050-11d1-b6bd-00c04fa372a7} {5175d334-c371-4806-b3ba-71fd53c9258d} {50dd5230-ba8a-11d1-bf5d-0000f805f530} {71a27cdd-812a-11d0-bec7-08002be2092f} {6d807884-7d21-11cf-801c-08002be10318} {88BAE032-5A81-49f0-BC3D-A4FF138216D6} {25dbce51-6c8f-4a72-8a6d-b54c2b4fc835} {eec5ad98-8080-425f-922a-dabf3de3f69a} {997b5d8d-c442-4f2e-baf3-9c8e671e9e21}


(for /F "tokens=*" %%G in ('reg query HKLM\System\CurrentControlSet\Enum\USB') DO (
    rem echo Found Key %%G
    rem get sub devices
    (for /F "tokens=*" %%H in ('reg query "%%G"') DO (
        rem echo Found sub key %%H
        rem get the classGUID of this device
        (for /F "usebackq tokens=3*" %%I in (`reg query "%%H" /v ClassGUID 2^>nul ^| find "REG_" `) DO (
            rem echo Found GUID: %%I
            rem see if this ID is in the list of bad devices
            (for %%D in (%bad_devices%) DO (
                rem echo checking %%I against %%D
                if "%%D"=="%%I" (
                    echo removing %%I ...
                    rem Remove the key
                    if "%debug_script%"=="false" (
                        reg delete "%%H" /f
                    )
                ) else (
                    rem echo .
                )
            ))
        ))
        
    ))
))


REM Mark that we have cleared the logs already
reg add "HKLM\Software\OPE\OPELMS\LOGS_CLEARED" /f /reg:64 2>nul


:skipclearlogs
