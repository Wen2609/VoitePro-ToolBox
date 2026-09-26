# -*- coding: utf-8 -*-
import subprocess, time, os, sys
sys.stdout.reconfigure(encoding='utf-8')
exe = r"D:\doubao space\VioletToolBox\VioletToolBox\bin\Debug\net8.0-windows\VioletToolBox.exe"
outdir = r"D:\doubao space\VioletToolBox\pages_v3"
os.makedirs(outdir, exist_ok=True)
cap_ps = r"D:\doubao space\VioletToolBox\scripts\cap_win.ps1"

pages = [
    ("BasicFlashView", "1_basic.png"),
    ("FastbootVisualizationView", "2_fastboot.png"),
    ("OujiaFlashView", "3_oujia.png"),
    ("EdlFlashView", "4_edl.png"),
    ("ColorOSAssistantView", "5_coloros.png"),
    ("HiddenEnvironmentView", "6_hidden.png"),
    ("SystemZoneView", "7_systemzone.png"),
    ("AutorootView", "8_autoroot.png"),
    ("AppManagementView", "9_appmgmt.png"),
    ("AndroidGeneralView", "10_android.png"),
    ("PayloadView", "11_payload.png"),
    ("BackupAssistantView", "12_backup.png"),
    ("RomDownloadview", "13_rom.png"),
    ("VioletDownloadView", "14_download.png"),
    ("AboutToolView", "15_about.png"),
]

for view, fname in pages:
    out = os.path.join(outdir, fname)
    proc = subprocess.Popen([exe, f"--page={view}"], cwd=os.path.dirname(exe))
    try:
        time.sleep(6.0)
        r = subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", cap_ps, "-Out", out],
                           capture_output=True, text=True, timeout=30)
        last = (r.stdout or "").strip().splitlines()
        print(f"{view}: {last[-1] if last else 'EMPTY'}")
    except Exception as e:
        print(f"{view}: ERROR {e}")
    finally:
        proc.kill()
        time.sleep(0.3)
print("ALL DONE")
