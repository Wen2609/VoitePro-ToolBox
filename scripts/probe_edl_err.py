# -*- coding: utf-8 -*-
import io, sys, re
sys.stdout.reconfigure(encoding='utf-8')
base = r'D:\doubao space\VioletToolBox\VioletToolBox'
cs = io.open(base + r'\MainWindow.xaml.cs', 'r', encoding='utf-8').read()
lines = cs.split('\n')
for ln in [4072, 14115, 18815, 18825, 18827, 19049]:
    print('=== L' + str(ln) + ' ===')
    for i in range(max(0, ln-4), min(len(lines), ln+3)):
        print(i+1, ':', lines[i].strip()[:110])
    print()
