# -*- coding: utf-8 -*-
import io, sys, re
sys.stdout.reconfigure(encoding='utf-8')
x = io.open(r'D:\doubao space\VioletToolBox\VioletToolBox\MainWindow.xaml', 'r', encoding='utf-8').read()
i = x.find('Name="HomeView"')
seg = x[:i]
print('pre-HomeView len:', len(seg))
names = []
for m in re.finditer(r'Name="([A-Za-z]+Button|[A-Za-z]+Group|[A-Za-z]+Item)"', seg):
    names.append(m.group(1))
print('sidebar buttons:', names)
# 查 EDL/edl 在 pre-HomeView 段
edl_positions = [m.start() for m in re.finditer(r'[Ee]dl', seg)]
print('EDL occurrences in pre-HomeView:', len(edl_positions))
for p in edl_positions[:10]:
    print('---', seg[max(0,p-120):p+180].replace('\n',' ')[:300])
