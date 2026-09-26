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

def root_grid_end(x, gi):
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

targets = ['Page_FastbootVisualizationView', 'Page_SystemZoneView', 'Page_PayloadView',
           'Page_RomDownloadview', 'Page_ColorOSAssistantView']
for key in targets:
    m = re.search(r'<DataTemplate x:Key="' + key + r'">', x)
    assert m, key + ' NOT FOUND'
    te = template_end(x, m.end())
    assert te != -1, key + ' template end NOT FOUND'
    seg = x[m.end():te]
    if '<ScrollViewer' in seg:
        print(key, 'already has ScrollViewer, skip')
        continue
    rm = re.search(r'<Grid\s+Name="' + key.replace('Page_', '') + r'"', seg)
    assert rm, key + ' root Grid NOT FOUND'
    gt = seg.find('>', rm.start())
    gi = m.end() + gt + 1
    ge = root_grid_end(x, gi)
    assert ge != -1, key + ' root grid end NOT FOUND'
    # 跳过 Grid.Resources（若有）：ScrollViewer 插在资源区之后
    res_close = x.find('</Grid.Resources>', gi)
    if res_close != -1 and res_close < ge:
        gi = res_close + len('</Grid.Resources>')
    open_tpl = '<ScrollViewer VerticalScrollBarVisibility="Auto" HorizontalScrollBarVisibility="Disabled" Padding="0,0,4,0">'
    x = x[:gi] + open_tpl + x[gi:ge] + '</ScrollViewer>' + x[ge:]
    print(key, 'wrapped after resources, span', ge - gi)
io.open(fp, 'w', encoding='utf-8', newline='').write(x)
print('done')
