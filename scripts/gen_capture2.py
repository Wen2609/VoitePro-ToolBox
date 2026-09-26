# -*- coding: utf-8 -*-
import io
nav = '"D:\\doubao space\\VioletToolBox\\scripts\\ui_nav4.ps1"'
groups = [
    ("实用功能", [("模块专区", "p16_module"), ("断点续传", "p17_resume"), ("文件传输", "p18_file"), ("脱机修补", "p19_offline"), ("Payload", "p20_payload")]),
    ("刷机资源", [("下载专区", "p13_download"), ("Rom专区", "p12_rom")]),
    ("刷写功能", [("降级助手", "p4_coloros")]),
]
lines = []
for grp, pages in groups:
    lines.append('powershell -ExecutionPolicy Bypass -File {0} -Name "{1}" -Out "D:\\doubao space\\VioletToolBox\\grp2.png" 2>&1 | ForEach-Object {{ $_.ToString() }} | Select-Object -Last 1'.format(nav, grp))
    lines.append('Start-Sleep 1')
    for name, out in pages:
        lines.append('powershell -ExecutionPolicy Bypass -File {0} -Name "{1}" -Out "D:\\doubao space\\VioletToolBox\\{2}.png" 2>&1 | ForEach-Object {{ $_.ToString() }} | Select-Object -Last 1'.format(nav, name, out))
        lines.append('Start-Sleep 1')
script = "\r\n".join(lines) + "\r\nWrite-Output 'DONE2'\r\n"
io.open(r'D:\doubao space\VioletToolBox\scripts\capture_rest.ps1', 'w', encoding='utf-8-sig', newline='\r\n').write(script)
print('capture_rest.ps1 regenerated')
