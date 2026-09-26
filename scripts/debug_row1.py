# -*- coding: utf-8 -*-
import io, re, sys
sys.stdout.reconfigure(encoding='utf-8')
x = io.open(r'D:\doubao space\VioletToolBox\VioletToolBox\MainWindow.xaml', 'r', encoding='utf-8').read()
m = re.search(r'<DataTemplate x:Key="Page_FastbootVisualizationView">', x)
te_m = re.search(r'</DataTemplate>', x[m.end():])
te = m.end() + te_m.start()
print('template end at', te - m.end(), 'chars in')
# 根 Grid
rm = re.search(r'<Grid\s+Name="FastbootVisualizationView"', x[m.end():])
gt = seg_find = m.end() + rm.start()
gt = x.find('>', gt)
root_start = gt + 1
r1 = re.search(r'<Grid\s+Grid\.Row="1"[^>]*>', x[root_start:te])
gi = root_start + r1.start()
gt1 = x.find('>', gi)
print('Row1 Grid open at', gt1 - m.end(), 'chars in, attrs:', x[gi:gt1+1][:120].replace('\n', ' '))
# 配对
G_OPEN = re.compile(r'<Grid[\s>]')
G_CLOSE = re.compile(r'</Grid>')
depth = 1; j = gt1 + 1; last = None; n = 0
while j < len(x):
    o = G_OPEN.search(x, j); c = G_CLOSE.search(x, j)
    if not o and not c: break
    if o and (not c or o.start() < c.start()):
        gt2 = x.find('>', o.start())
        if gt2 != -1 and x[gt2-1] == '/':
            j = gt2 + 1; continue
        depth += 1; j = o.end()
    else:
        depth -= 1; n += 1
        if depth <= 0:
            print('Row1 Grid CLOSE at', c.start() - m.end(), 'chars in')
            break
        j = c.end()
if depth != 0:
    print('UNBALANCED: depth', depth, 'at end of template', te - m.end())
    # 打印模板末尾 500 字符
    print('TAIL:', x[te-500:te][:500].replace('\n', ' ')[-500:])
