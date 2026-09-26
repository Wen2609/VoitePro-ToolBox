@echo off
setlocal EnableExtensions

cd /d "%~dp0"

set "BOOT=%~1"
if "%BOOT%"=="" set "BOOT=boot.img"

set "KERNEL=%~2"
if "%KERNEL%"=="" set "KERNEL=Image"

set "PATCH_DTB=1"
set "PATCH_INITRAMFS=0"
for %%A in (%*) do (
  if /I "%%~A"=="--no-patch-dtb" set "PATCH_DTB=0"
  if /I "%%~A"=="--want-initramfs" set "PATCH_INITRAMFS=1"
)

set "MAGISKBOOT=magiskboot.exe"

if not exist "%MAGISKBOOT%" (
  echo [ERROR] magiskboot.exe not found
  echo Run from directory containing magiskboot.exe
  pause
  exit /b 1
)

if not exist "%BOOT%" (
  echo [ERROR] boot image not found: "%BOOT%"
  echo Usage: repack_boot.bat [boot.img] [Image|Image.gz|Image.lz4|Image.xz|zImage]
  echo Example: repack_boot.bat boot.img Image
  pause
  exit /b 1
)

echo [INFO] Unpacking "%BOOT%"
"%MAGISKBOOT%" unpack "%BOOT%"
if errorlevel 1 (
  echo [ERROR] Unpack failed
  pause
  exit /b 1
)

if "%PATCH_DTB%"=="1" (
  if exist "dtb" (
    echo [INFO] Patching dtb (remove verity/avb)
    "%MAGISKBOOT%" dtb "dtb" patch || (
      echo [WARN] dtb patch failed
    )
  )
  if exist "kernel_dtb" (
    echo [INFO] Patching kernel_dtb (remove verity/avb)
    "%MAGISKBOOT%" dtb "kernel_dtb" patch || (
      echo [WARN] kernel_dtb patch failed
    )
  )
)

set "COPIED=0"
if exist "%KERNEL%" (
  echo [INFO] Using "%KERNEL%"
  copy /y "%KERNEL%" "kernel" >nul
  if errorlevel 1 (
    echo [ERROR] Copy failed
    pause
    exit /b 1
  )
  set "COPIED=1"
)

if "%COPIED%"=="0" if exist "Image.gz" (
  echo [INFO] Using "Image.gz"
  "%MAGISKBOOT%" decompress "Image.gz" "kernel"
  if errorlevel 1 (
    echo [ERROR] Decompress failed
    pause
    exit /b 1
  )
  set "COPIED=1"
)

if "%COPIED%"=="0" if exist "Image.lz4" (
  echo [INFO] Using "Image.lz4"
  "%MAGISKBOOT%" decompress "Image.lz4" "kernel"
  if errorlevel 1 (
    echo [ERROR] Decompress failed
    pause
    exit /b 1
  )
  set "COPIED=1"
)

if "%COPIED%"=="0" if exist "Image.xz" (
  echo [INFO] Using "Image.xz"
  "%MAGISKBOOT%" decompress "Image.xz" "kernel"
  if errorlevel 1 (
    echo [ERROR] Decompress failed
    pause
    exit /b 1
  )
  set "COPIED=1"
)

if "%COPIED%"=="0" if exist "zImage" (
  echo [INFO] Using "zImage"
  "%MAGISKBOOT%" decompress "zImage" "kernel"
  if errorlevel 1 (
    echo [ERROR] Decompress failed
    pause
    exit /b 1
  )
  set "COPIED=1"
)

if "%COPIED%"=="0" (
  echo [ERROR] Kernel file not found: "%KERNEL%" or known variants
  echo Usage: repack_boot.bat [boot.img] [Image|Image.gz|Image.lz4|Image.xz|zImage]
  echo Example: repack_boot.bat boot.img Image
  pause
  exit /b 1
)

if "%PATCH_INITRAMFS%"=="1" (
  echo [INFO] Hexpatch kernel skip_initramfs -> want_initramfs
  "%MAGISKBOOT%" hexpatch "kernel" 736B69705F696E697472616D6673 77616E745F696E697472616D6673 || (
    echo [WARN] hexpatch failed
  )
)

echo [INFO] Repacking to "boot-new.img"
"%MAGISKBOOT%" repack "%BOOT%" "boot-new.img"
if errorlevel 1 (
  echo [ERROR] Repack failed
  pause
  exit /b 1
)

echo [INFO] Success: "boot-new.img" generated
exit /b 0

