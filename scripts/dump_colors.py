# -*- coding: utf-8 -*-
import re
c = open(r'D:\doubao space\VioletToolBox\VioletToolBox\Themes\Colors.xaml', encoding='utf-8').read()
out = []
for m in re.finditer(r'x:Key="([^"]+)"\s+Color="([^"]+)"', c):
    out.append('%s = %s' % (m.group(1), m.group(2)))
open(r'D:\doubao space\VioletToolBox\colors_dump.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('keys:', len(out))
# 也查 MainWindow 侧边栏主题色
mw = open(r'D:\doubao space\VioletToolBox\VioletToolBox\MainWindow.xaml', encoding='utf-8').read()
for pat in ['#FF0A84FF', '#0A84FF', '#09488A', '#E0EFFF']:
    print(pat, 'count in MainWindow:', mw.count(pat))
