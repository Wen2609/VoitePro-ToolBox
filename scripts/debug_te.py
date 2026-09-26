# -*- coding: utf-8 -*-
import io, re, sys
sys.stdout.reconfigure(encoding='utf-8')
x = io.open(r'D:\doubao space\VioletToolBox\VioletToolBox\MainWindow.xaml', 'r', encoding='utf-8').read()
DT_OPEN = re.compile(r'<DataTemplate[\s>]')
DT_CLOSE = re.compile(r'</DataTemplate>')
m = re.search(r'<DataTemplate x:Key="Page_FastbootVisualizationView">', x)
depth = 0; j = m.end(); events = []
while j < len(x):
    o = DT_OPEN.search(x, j); c = DT_CLOSE.search(x, j)
    if not o and not c: break
    if o and (not c or o.start() < c.start()):
        depth += 1; events.append(('O', depth, o.start()-m.end())); j = o.end()
    else:
        depth -= 1; events.append(('C', depth, c.start()-m.end())); j = c.end()
        if depth == 0:
            print('template close at', c.start()-m.end(), 'chars in')
            break
print('final depth', depth)
for e in events:
    print(e)
