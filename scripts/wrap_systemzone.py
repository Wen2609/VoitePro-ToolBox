# -*- coding: utf-8 -*-
import io, re, sys
sys.stdout.reconfigure(encoding='utf-8')
fp = r'D:\doubao space\VioletToolBox\VioletToolBox\MainWindow.xaml'
x = io.open(fp, 'r', encoding='utf-8').read()

G_OPEN = re.compile(r'<Grid[\s>]')
G_CLOSE = re.compile(r'</Grid>')

def grid_end(x, gi):
    depth = 1
    j = gi
    while j < len(x):
        o = G_OPEN.search(x, j); c = G_CLOSE.search(x, j)
        if not o and not c: return -1
        if o and (not c or o.start() < c.start()):
            gt = x.find('>', o.start())
            if gt != -1 and x[gt-1] == '/':
                j = gt + 1; continue
            depth += 1; j = o.end()
        else:
            depth -= 1; j = c.end()
            if depth == 0: return c.start()
    return -1

# SystemZoneView 根 Grid 内 Row1 Grid
m = re.search(r'<Grid\s+Name="SystemZoneView"', x)
gt = x.find('>', m.end())
root_start = gt + 1
r1 = re.search(r'<Grid\s+Grid\.Row="1"', x[root_start:])
assert r1, 'Row1 Grid NOT FOUND'
gi = root_start + r1.start()
gt1 = x.find('>', gi)
gi_after = gt1 + 1
ge = grid_end(x, gi_after)
assert ge != -1, 'Row1 grid end NOT FOUND'
open_tpl = '<ScrollViewer VerticalScrollBarVisibility="Auto" HorizontalScrollBarVisibility="Disabled">'
x = x[:gi_after] + open_tpl + x[gi_after:ge] + '</ScrollViewer>' + x[ge:]
io.open(fp, 'w', encoding='utf-8', newline='').write(x)
print('SystemZone Row1 wrapped, span', ge - gi_after)
