# -*- coding: utf-8 -*-
import io, re, sys
sys.stdout.reconfigure(encoding='utf-8')
x = io.open(r'D:\doubao space\VioletToolBox\VioletToolBox\MainWindow.xaml', 'r', encoding='utf-8').read()
m = re.search(r'<DataTemplate x:Key="Page_FastbootVisualizationView">', x)
print('template at', m.start())
# 模板内 Grid 配对
depth = 0; j = m.end(); found = []
while j < len(x):
    o = x.find('<Grid', j); c = x.find('</Grid>', j)
    if o == -1 and c == -1: break
    if o != -1 and (c == -1 or o < c):
        gt = x.find('>', o)
        if gt != -1 and x[gt-1] == '/':
            j = gt + 1; continue
        depth += 1
        nm = re.search(r'Name="([^"]*)"', x[o:gt])
        found.append(('open', depth, nm.group(1) if nm else ''))
        j = o + 5
    else:
        depth -= 1
        found.append(('close', depth, ''))
        j = c + 7
        if depth == 0:
            break
for f in found:
    print(f)
print('final depth', depth, 'end', j)
