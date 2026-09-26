# -*- coding: utf-8 -*-
"""1) 重跑 lazy_cs2（幂等补漏，修复插值字符串词法） 2) 处理 DownloadZone 残留块"""
import io, re, sys
sys.stdout.reconfigure(encoding='utf-8')

# 1) 重跑 lazy_cs2
exec(io.open(r'D:\doubao space\VioletToolBox\lazy_cs2.py', 'r', encoding='utf-8').read())
print('lazy_cs2 rerun done')

# 2) DownloadZone 残留块 → ShowPage("VioletDownloadView")
fp = r'D:\doubao space\VioletToolBox\VioletToolBox\MainWindow.xaml.cs'
cs = io.open(fp, 'r', encoding='utf-8').read()
pat = re.compile(
    r'if \(homeView != null\) homeView\.Visibility = Visibility\.Collapsed;\n'
    r'(?:.*?)\n'
    r'\s*if \(violetDownloadView != null\) violetDownloadView\.Visibility = Visibility\.\w+;',
    re.DOTALL)
ms = list(pat.finditer(cs))
print('downloadzone leftover blocks:', len(ms))
if ms:
    for m in reversed(ms):
        cs = cs[:m.start()] + 'ShowPage("VioletDownloadView");' + cs[m.end():]
    io.open(fp, 'w', encoding='utf-8', newline='').write(cs)
    print('replaced')
else:
    print('no leftover (already fine)')
