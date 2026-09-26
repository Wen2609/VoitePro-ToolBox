# -*- coding: utf-8 -*-
import io
nav = '"D:\\doubao space\\VioletToolBox\\scripts\\ui_nav4.ps1"'
# (分组, [(页面, 输出)])
groups = [
    ("刷写功能", [("基本刷入", "p1_basic"), ("可视刷写", "p2_fastboot"), ("欧加线刷", "p3_oujia"), ("EDL刷写", "p14_edl"), ("降级助手", "p4_coloros")]),
    ("实用功能", [("隐藏环境", "p5_hidden"), ("系统分区", "p6_systemzone"), ("自动root", "p7_autoroot"), ("应用管理", "p8_appmgmt"), ("安卓通用", "p9_android"), ("payload", "p10_payload"), ("备份助手", "p11_backup")]),
    ("刷机资源", [("Rom专区", "p12_rom"), ("下载专区", "p13_download")]),
]
lines = []
for grp, pages in groups:
    lines.append('powershell -ExecutionPolicy Bypass -File {0} -Name "{1}" -Out "D:\\doubao space\\VioletToolBox\\grp.png" 2>&1 | ForEach-Object {{ $_.ToString() }} | Select-Object -Last 1'.format(nav, grp))
    lines.append('Start-Sleep 1')
    for name, out in pages:
        lines.append('powershell -ExecutionPolicy Bypass -File {0} -Name "{1}" -Out "D:\\doubao space\\VioletToolBox\\{2}.png" 2>&1 | ForEach-Object {{ $_.ToString() }} | Select-Object -Last 1'.format(nav, name, out))
        lines.append('Start-Sleep 1')
script = "\r\n".join(lines) + "\r\nWrite-Output 'ALL DONE'\r\n"
io.open(r'D:\doubao space\VioletToolBox\scripts\capture_all.ps1', 'w', encoding='utf-8-sig', newline='\r\n').write(script)
print('regenerated with group expansion')
