# -*- coding: utf-8 -*-
import io, re, sys
sys.stdout.reconfigure(encoding='utf-8')
x = io.open(r'D:\doubao space\VioletToolBox\VioletToolBox\MainWindow.xaml', 'r', encoding='utf-8').read()
tpls = [(m2.group(1), m2.start()) for m2 in re.finditer(r'<DataTemplate\s+x:Key="(?:DISABLED_)?(Page_[A-Za-z0-9]+)"', x)]
out = []
for i, (key, pos) in enumerate(tpls):
    end = tpls[i+1][1] if i+1 < len(tpls) else len(x)
    seg = x[pos:end]
    svg = len(re.findall(r'<svg:', seg))
    hc = len(re.findall(r'<hc:', seg))
    # HandyControl 具体控件名
    hcs = sorted(set(re.findall(r'<hc:([A-Za-z]+)', seg)))
    out.append('%s svg=%d hc=%d hcs=%s' % (key, svg, hc, ','.join(hcs[:12])))
io.open(r'D:\doubao space\VioletToolBox\tpl_cmp.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('done')
