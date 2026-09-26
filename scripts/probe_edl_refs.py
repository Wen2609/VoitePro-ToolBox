# -*- coding: utf-8 -*-
import io, sys, re
sys.stdout.reconfigure(encoding='utf-8')
import os
base = r'D:\doubao space\VioletToolBox\VioletToolBox'
files = [f for f in os.listdir(base) if f.endswith('.cs')]
# 在 EdlFlash.cs 中定义的方法/字段名
edl = io.open(os.path.join(base, 'MainWindow.EdlFlash.cs'), 'r', encoding='utf-8').read()
# 方法定义名
defs = set(re.findall(r'(?:private|internal|public|protected)\s+(?:static\s+)?(?:async\s+)?[\w<>\[\],\s]+\s+([A-Za-z_]\w*)\s*\(', edl))
defs |= set(re.findall(r'private\s+readonly\s+[\w<>\[\],\s]+\s+(_edl\w+|EdlPort\w+|_edlPort\w+|EdlCloud\w+|EdlBug\w+)', edl))
print('== candidate EDL members ==')
print(sorted(list(defs))[:80])
# 其他 cs 文件引用这些成员吗
print('\n== cross-file refs ==')
for f in files:
    if f in ('MainWindow.EdlFlash.cs', 'MainWindow.EdlSession.cs', 'MainWindow.EdlDynamicSuper.cs', 'MainWindow.EdlFeedback.cs', 'EdlBuildPropReader.cs'):
        continue
    c = io.open(os.path.join(base, f), 'r', encoding='utf-8').read()
    hits = [d for d in defs if re.search(r'\b' + re.escape(d) + r'\b', c)]
    if hits:
        print(f, '->', sorted(hits)[:15])
