# -*- coding: utf-8 -*-
import io, re, sys
sys.stdout.reconfigure(encoding='utf-8')
fp = r'D:\doubao space\VioletToolBox\VioletToolBox\MainWindow.xaml'
x = io.open(fp, 'r', encoding='utf-8').read()
tpls = [(m2.group(1), m2.start()) for m2 in re.finditer(r'<DataTemplate\s+x:Key="(?:DISABLED_)?(Page_[A-Za-z0-9]+)"', x)]
for i, (key, pos) in enumerate(tpls):
    if key == 'Page_AutorootView':
        end = tpls[i+1][1] if i+1 < len(tpls) else len(x)
        seg = x[pos:end]
        out = []
        # 提取模板完整内容（从 <DataTemplate 到 </DataTemplate>）
        m = re.match(r'<DataTemplate\s+x:Key="Page_AutorootView">(.*)</DataTemplate>', seg, re.S)
        if m:
            body = m.group(1)
            inner_start = seg.find('<Grid', m.start())
            out.append('body start at %d, first 200: %s' % (inner_start, seg[inner_start:inner_start+200].replace('\n',' ')))
            io.open(r'D:\doubao space\VioletToolBox\autoroot_body.txt', 'w', encoding='utf-8').write(body)
            print('body extracted len=', len(body))
        break
