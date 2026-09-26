# -*- coding: utf-8 -*-
import subprocess, sys, time
pages = [
    ("主页", "c_home.png"),
    ("基本刷入", "c1_basic.png"),
    ("可视刷写", "c2_fastboot.png"),
    ("欧加线刷", "c3_oujia.png"),
    ("EDL刷写", "c4_edl.png"),
    ("降级助手", "c5_coloros.png"),
    ("隐藏环境", "c6_hidden.png"),
    ("系统分区", "c7_systemzone.png"),
    ("自动root", "c8_autoroot.png"),
    ("应用管理", "c9_appmgmt.png"),
    ("安卓通用", "c10_android.png"),
    ("payload", "c11_payload.png"),
    ("备份助手", "c12_backup.png"),
    ("Rom专区", "c13_rom.png"),
    ("下载专区", "c14_download.png"),
]
outdir = r"D:\doubao space\VioletToolBox\pages_v2"
import os
os.makedirs(outdir, exist_ok=True)
script = r"D:\doubao space\VioletToolBox\scripts\ui_nav5.ps1"
for name, f in pages:
    out = os.path.join(outdir, f)
    r = subprocess.run(
        ["powershell", "-ExecutionPolicy", "Bypass", "-File", script, "-Name", name, "-Out", out],
        capture_output=True, text=True, timeout=60
    )
    last = (r.stdout or "").strip().splitlines()
    print(f"{name}: {last[-1] if last else 'EMPTY'}")
    time.sleep(0.5)
print("ALL DONE")
