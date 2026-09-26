@ECHO OFF
mode con cols=71 lines=71
COLOR 0F
TITLE 紫罗兰工具箱命令行

set "SHORTCUT_1=fastboot oem set-gpu-preemption 0 androidboot.selinux=permissive"
set "SHORTCUT_2=fastboot oem set-gpu-preemption 0 androidboot.selinux=enforcing"
set "SHORTCUT_3=fastboot continue"

:CMD
CLS
ECHOC {0E}=--------------------------------------------------------------------={0F}{\n}
ECHO.
ECHOC {0C}                          紫罗兰工具箱命令行                                                           {0F}{\n}
ECHOC {0E}=--------------------------------------------------------------------={0F}{\n}
ECHO.
ECHO.
ECHOC {0A} ADB命令{0F}   adb devices                       检查设备连接{\n}
ECHOC            adb reboot recovery               重启到recovery模式{\n}
ECHOC            adb reboot bootloader             重启到fastboot模式{\n}
ECHOC {0E}=-------------------------------------------------------------------={0F}{\n}
ECHOC {0A} FASTBOOT{0F}  fastboot reboot                   重启{\n}
ECHOC            fastboot devices                  检查设备连接{\n}
ECHOC            fastboot oem edl                  进入9008模式{\n}
ECHOC            fastboot flash boot               刷入boot分区{\n}
ECHOC            fastboot set_active a/b           切换ab分区{\n}
ECHOC            fastboot flash init_boot          刷入init_boot分区{\n}
ECHOC            fastboot flash recovery           刷入TWRP{\n}
ECHOC            fastboot reboot recovery          重启到recovery模式{\n}
ECHOC            fastboot reboot bootloader        重启到fastboot模式{\n}
ECHOC            fastboot flashing unlock/lock     解锁/回锁BL{\n}
ECHOC            fastboot oem device-info          false为解锁，true为锁定{\n}
ECHOC {0E}=-------------------------------------------------------------------={0F}{\n}
ECHOC {0A} 快捷命令{0F}  1. 切换为宽容模式{\n}
ECHOC            2. 切换为严格模式{\n}
ECHOC            3. 退出Bootloader至开机{\n}
ECHOC {0B}=--------------------------------------------------------------------={0F}{\n}
ECHO.

:CMD-CONTINUE
ECHOC {0B}=--------------------------------------------------------------------={0F}{\n}
ECHOC {0E}[请输入命令]{0F}
set /p cmd=

if "%cmd%"=="v" (
    tasklist | find "mmc.exe" 1>nul 2>nul && ECHOC {0A}                                                 [设备管理器已打开]{0F}{\n}&& goto CMD-CONTINUE
    start %windir%\system32\devmgmt.msc & goto CMD-CONTINUE
)

if "%cmd%"=="1" (
    %SHORTCUT_1%
    if %ERRORLEVEL% EQU 0 (
        ECHOC {0A}                                                    [已切换为宽容模式]{0F}{\n}
    ) else (
        ECHOC {0C}                                                    [切换失败]{0F}{\n}
    )
    goto CMD-CONTINUE
)

if "%cmd%"=="2" (
    %SHORTCUT_2%
    if %ERRORLEVEL% EQU 0 (
        ECHOC {0A}                                                    [已切换为严格模式]{0F}{\n}
    ) else (
        ECHOC {0C}                                                    [切换失败]{0F}{\n}
    )
    goto CMD-CONTINUE
)

if "%cmd%"=="3" (
    %SHORTCUT_3%
    if %ERRORLEVEL% EQU 0 (
        ECHOC {0A}                                          [已退出Bootloader并继续开机]{0F}{\n}
    ) else (
        ECHOC {0C}                                                    [执行失败]{0F}{\n}
    )
    goto CMD-CONTINUE
)

if /I "%cmd%"=="adb reboot bootloader" (
    adb reboot bootloader
    ECHOC {0A}                                              [正在重启到fastboot模式]{0F}{\n}
    goto CMD-CONTINUE
)

if "%cmd%"=="" (
    ECHOC {0C}                                                    [命令不能为空]{0F}{\n}
    goto CMD-CONTINUE
)

if "%cmd%"=="cls" goto CMD
if "%cmd%"=="CLS" goto CMD
if "%cmd%"=="exit" exit
if "%cmd%"=="EXIT" exit
if "%cmd%"=="cc" goto CMD-CONTINUE

rem 执行用户输入的命令
cmd /c "%cmd%"
set "RET=%ERRORLEVEL%"

if "%RET%"=="0" (
    ECHOC {0A}                                                         [命令执行成功]{0F}{\n}
) else (
    ECHOC {0C}                                                         [命令执行失败]{0F}{\n}
)
goto CMD-CONTINUE