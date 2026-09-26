# -*- coding: utf-8 -*-
import io, sys
sys.stdout.reconfigure(encoding='utf-8')
x = io.open(r'D:\doubao space\VioletToolBox\VioletToolBox\MainWindow.xaml', 'r', encoding='utf-8').read()
i = x.find('Name="HomeView"')
seg = x[i-12000:i]
# 找所有 SideMenuItem 的 Name/Header
import re
for m in re.finditer(r'<hc:SideMenuItem[^>]*>|<hc:SideMenuItem\s+Name="[^"]*"[^>]*>', seg):
    s = m.group(0)
    nm = re.search(r'Name="([^"]*)"', s)
    print('ITEM:', nm.group(1) if nm else '?')
# 打印 EDL 相关上下文
j = seg.find('Edl')
while j != -1 and j < len(seg):
    print('--- EDL ctx ---')
    print(seg[max(0,j-200):j+300].replace('\n',' ')[:500])
    j = seg.find('Edl', j+1)
    if j > 12000: break
