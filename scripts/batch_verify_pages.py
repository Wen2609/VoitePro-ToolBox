# -*- coding: utf-8 -*-
"""批量验证页面：逐个启动 -page=XxxView 并截图。结果写入 verify_summary.txt"""
import subprocess, time, os, sys

EXE = r"D:\doubao space\VioletToolBox\VioletToolBox\bin\Debug\net8.0-windows\VioletToolBox.exe"
CAP = r"D:\doubao space\VioletToolBox\scripts\cap_win2.ps1"
OUT_DIR = r"D:\doubao space\VioletToolBox"

pages = [
    ("HomeView", "ui_home.png"),
    ("ScreenMirrorView", "ui_touping.png"),
    ("BasicFlashView", "ui_jibenshuru.png"),
    ("FastbootVisualizationView", "ui_keshi.png"),
    ("OujiaFlashView", "ui_oujia.png"),
    ("EdlFlashView", "ui_edl.png"),
    ("ColorOSAssistantView", "ui_jiangji.png"),
    ("HiddenEnvironmentView", "ui_yincang.png"),
    ("SystemZoneView", "ui_xitongqu.png"),
    ("AutorootView", "ui_autoroot.png"),
    ("AppManagementView", "ui_app.png"),
    ("AndroidGeneralView", "ui_anzhuo.png"),
    ("PayloadView", "ui_payload.png"),
    ("RomDownloadview", "ui_rom.png"),
    ("BackupAssistantView", "ui_beifen.png"),
    ("VioletDownloadView", "ui_ziliaodownload.png"),
    ("AboutToolView", "ui_guanyu.png"),
]

results = []
for i, (page, out) in enumerate(pages):
    subprocess.run(["taskkill", "/F", "/IM", "VioletToolBox.exe"],
                   capture_output=True, shell=True)
    time.sleep(1.2)
    p = subprocess.Popen([EXE, "-page=" + page])
    time.sleep(11)
    alive = p.poll() is None
    if not alive:
        results.append(f"{page}: CRASHED")
        continue
    # 截图
    r = subprocess.run(
        ["powershell", "-NoProfile", "-Command",
         f"& '{CAP}' -TargetPid {p.pid} -Out '{OUT_DIR}\\{out}'"],
        capture_output=True, shell=True)
    time.sleep(0.5)
    ok = os.path.exists(os.path.join(OUT_DIR, out)) and os.path.getsize(os.path.join(OUT_DIR, out)) > 10000
    results.append(f"{page}: {'OK' if ok else 'CAPFAIL'} {out}")

with open(os.path.join(OUT_DIR, "verify_summary.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(results))
print("\n".join(results))
