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

# 目标模板及其 Row1 内容 Grid 特征（name 或 列定义）
targets = [
    ('Page_FastbootVisualizationView', 'FastbootVisualizationView'),
    ('Page_OujiaFlashView', 'OujiaFlashView'),
    ('Page_PayloadView', 'PayloadView'),
    ('Page_AndroidGeneralView', 'AndroidGeneralView'),
]
for tkey, rootname in targets:
    m = re.search(r'<DataTemplate x:Key="' + tkey + r'">', x)
    assert m, tkey + ' NOT FOUND'
    te = template_end(x, m.start())  # 从模板开标签起配对（含自身）
    seg = x[m.end():te]
    if '<ScrollViewer' in seg:
        print(tkey, 'ALREADY has ScrollViewer, skip')
        continue
    # 根 Grid
    rm = re.search(r'<Grid\s+Name="' + rootname + r'"', seg)
    assert rm, tkey + ' root Grid NOT FOUND'
    gt = seg.find('>', rm.start())
    root_start = m.end() + gt + 1
    # 找 Row1 内容 Grid：第一个 <Grid Grid.Row="1"（属性元素后的内容 Grid）
    r1 = re.search(r'<Grid\s+Grid\.Row="1"[^>]*>', x[root_start:te])
    if not r1:
        print(tkey, 'NO Row1 Grid')
        continue
    gi = root_start + r1.start()
    gt1 = x.find('>', gi)
    gi_after = gt1 + 1
    ge = grid_end(x, gi_after)
    assert ge != -1 and ge < te, tkey + ' row1 grid end NOT FOUND'
    inner = x[gi_after:ge]
    # 跳过 Row1 Grid 自身属性元素（Resources/RowDefs/ColDefs/Triggers）→ ScrollViewer 插在属性元素后
    prop_end = gi_after
    for prop in ('Grid.Resources', 'Grid.RowDefinitions', 'Grid.ColumnDefinitions', 'Grid.Triggers'):
        o = x.find('<' + prop + '>', prop_end)
        if o != -1 and o < ge:
            c = x.find('</' + prop + '>', o)
            if c != -1 and c < ge:
                prop_end = c + len('</' + prop + '>')
    open_tpl = '<ScrollViewer Grid.Row="1" VerticalScrollBarVisibility="Auto" HorizontalScrollBarVisibility="Disabled">'
    x = x[:prop_end] + open_tpl + x[prop_end:ge] + '</ScrollViewer>' + x[ge:]
    print(tkey, 'wrapped row1 content, span', ge - prop_end)
io.open(fp, 'w', encoding='utf-8', newline='').write(x)
print('done')
