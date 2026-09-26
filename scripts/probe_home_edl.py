# -*- coding: utf-8 -*-
import io, sys, re
sys.stdout.reconfigure(encoding='utf-8')
x = io.open(r'D:\doubao space\VioletToolBox\VioletToolBox\MainWindow.xaml', 'r', encoding='utf-8').read()
# HomeView 内 EDL
i = x.find('Name="HomeView"')
j = x.find('Name="PageHost"')
seg = x[i:j]
print('HomeView len:', len(seg))
for m in re.finditer(r'.{150}EdlFlashView.{150}', seg):
    print('--- EDL ctx ---')
    print(m.group(0).replace('\n', ' ')[:350])
# 主页卡片跳转：找 ShowPage("EdlFlashView")
for m in re.finditer(r'.{100}EdlFlashView.{100}', x):
    print('--- EDL any ctx ---')
    print(m.group(0).replace('\n', ' ')[:300])
