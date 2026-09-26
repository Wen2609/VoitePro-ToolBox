# -*- coding: utf-8 -*-
import io, sys, re
sys.stdout.reconfigure(encoding='utf-8')
x = io.open(r'D:\doubao space\VioletToolBox\VioletToolBox\MainWindow.xaml', 'r', encoding='utf-8').read()
# 模板根 Grid：<Grid Name="XxxView" ... VerticalAlignment="Top" -> 移除 VerticalAlignment（默认 Stretch）
fixed = 0
for key in ['AboutToolView', 'OujiaFlashView', 'AutorootView', 'ColorOSAssistantView', 'VioletDownloadView']:
    pat = re.compile(r'(<DataTemplate x:Key="Page_' + key + r'">\s*<Grid\s+Name="' + key + r'"[^>]*?)\s*VerticalAlignment="Top"', re.S)
    m = pat.search(x)
    if m:
        x = x[:m.start()] + m.group(1) + x[m.end():]
        fixed += 1
print('root grids VA=Top removed:', fixed)
io.open(r'D:\doubao space\VioletToolBox\VioletToolBox\MainWindow.xaml', 'w', encoding='utf-8', newline='').write(x)
