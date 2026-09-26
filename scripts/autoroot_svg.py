# -*- coding: utf-8 -*-
import io, re, sys
sys.stdout.reconfigure(encoding='utf-8')
x = io.open(r'D:\doubao space\VioletToolBox\VioletToolBox\MainWindow.xaml', 'r', encoding='utf-8').read()
tpls = [(m2.group(1), m2.start()) for m2 in re.finditer(r'<DataTemplate\s+x:Key="(?:DISABLED_)?(Page_[A-Za-z0-9]+)"', x)]
out = []
for i, (key, pos) in enumerate(tpls):
    if key == 'Page_AutorootView':
        end = tpls[i+1][1] if i+1 < len(tpls) else len(x)
        seg = x[pos:end]
        for j, m in enumerate(re.finditer(r'<svg:\w+[^>]*>', seg)):
            out.append('SVG#%d: %s' % (j, m.group(0)[:250].replace('\n', ' ')))
io.open(r'D:\doubao space\VioletToolBox\autoroot_svg.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('svg count:', len(out))
