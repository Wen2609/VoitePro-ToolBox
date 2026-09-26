# -*- coding: utf-8 -*-
import io, re, sys
sys.stdout.reconfigure(encoding='utf-8')
fp = r'D:\doubao space\VioletToolBox\VioletToolBox\MainWindow.xaml'
x = io.open(fp, 'r', encoding='utf-8').read()

DT_OPEN = re.compile(r'<DataTemplate[\s>]')
DT_CLOSE = re.compile(r'</DataTemplate>')
G_OPEN = re.compile(r'<Grid[\s>]')
G_CLOSE = re.compile(r'</Grid>')

def template_end(x, i):
    depth = 0; j = i
    while j < len(x):
        o = DT_OPEN.search(x, j); c = DT_CLOSE.search(x, j)
        if not o and not c: return -1
        if o and (not c or o.start() < c.start()):
            depth += 1; j = o.end()
        else:
            depth -= 1; j = c.end()
            if depth == 0: return j
    return -1

def grid_end(x, gi):
    depth = 1; j = gi
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

targets = [
    ('Page_FastbootVisualizationView', 'FastbootVisualizationView'),
    ('Page_PayloadView', 'PayloadView'),
]
for tkey, rootname in targets:
    m = re.search(r'<DataTemplate x:Key="' + tkey + r'">', x)
    assert m, tkey + ' NOT FOUND'
    te = template_end(x, m.start())
    seg = x[m.end():te]
    if '<ScrollViewer Grid.Row="1"' in seg:
        print(tkey, 'already wrapped, skip')
        continue
    rm = re.search(r'<Grid\s+Name="' + rootname + r'"', seg)
    assert rm, tkey + ' root Grid NOT FOUND'
    gt = seg.find('>', rm.start())
    root_start = m.end() + gt + 1
    r1 = re.search(r'<Grid\s+Grid\.Row="1"[^>]*>', x[root_start:te])
    assert r1, tkey + ' NO Row1 Grid'
    gi = root_start + r1.start()
    ge = grid_end(x, gi)
    assert ge != -1 and ge < te, tkey + ' row1 end NOT FOUND'
    open_tpl = '<ScrollViewer Grid.Row="1" VerticalScrollBarVisibility="Auto" HorizontalScrollBarVisibility="Disabled">'
    x = x[:gi] + open_tpl + x[gi:ge] + '</ScrollViewer>' + x[ge:]
    print(tkey, 'wrapped whole row1 grid, span', ge - gi)
io.open(fp, 'w', encoding='utf-8', newline='').write(x)
print('done')
