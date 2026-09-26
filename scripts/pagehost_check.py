# -*- coding: utf-8 -*-
import io, re, sys
sys.stdout.reconfigure(encoding='utf-8')
x = io.open(r'D:\doubao space\VioletToolBox\VioletToolBox\MainWindow.xaml', 'r', encoding='utf-8').read()
# 找 PageHost 和主内容区（HomeView 在主内容区）
out = []
for m in re.finditer(r'<ContentControl[^>]*x:Name="PageHost"[^>]*>', x):
    out.append('PageHost at L%d: %s' % (x[:m.start()].count('\n') + 1, m.group(0)[:250]))
# 找 PageHost 之后的结构（主内容区）
mh = re.search(r'x:Name="PageHost"[^>]*>', x)
if mh:
    pos = mh.end()
    seg = x[pos:pos+2000]
    out.append('AFTER PageHost: ' + seg.replace('\n', ' ')[:500])
# 找 HomeView 在主内容区的位置（Window 直接子级）
for m in re.finditer(r'<Grid\s+Name="HomeView"', x):
    out.append('HomeView Grid at L%d' % (x[:m.start()].count('\n') + 1))
io.open(r'D:\doubao space\VioletToolBox\pagehost_check.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('done')
