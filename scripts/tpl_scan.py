# -*- coding: utf-8 -*-
import io, re, sys
sys.stdout.reconfigure(encoding='utf-8')
x = io.open(r'D:\doubao space\VioletToolBox\VioletToolBox\MainWindow.xaml', 'r', encoding='utf-8').read()
# 找 AutorootView 模板段
m = re.search(r'<DataTemplate\s+x:Key="(?:DISABLED_)?(Page_[A-Za-z0-9]+)"', x)
tpls = [(m2.group(1), m2.start()) for m2 in re.finditer(r'<DataTemplate\s+x:Key="(?:DISABLED_)?(Page_[A-Za-z0-9]+)"', x)]
out = []
for i, (key, pos) in enumerate(tpls):
    end = tpls[i+1][1] if i+1 < len(tpls) else len(x)
    seg = x[pos:end]
    out.append('%s: chars=%d, lines=%d' % (key, len(seg), seg.count('\n')))
io.open(r'D:\doubao space\VioletToolBox\tpl_size.txt', 'w', encoding='utf-8').write('\n'.join(out))
# AutorootView 段特殊内容
for i, (key, pos) in enumerate(tpls):
    if key == 'Page_AutorootView':
        end = tpls[i+1][1] if i+1 < len(tpls) else len(x)
        seg = x[pos:end]
        specials = []
        for pat, nm in [(r'<Storyboard', 'Storyboard'), (r'EventTrigger', 'EventTrigger'), (r'<hc:', 'HandyControl'), (r'HorizontalBattery', 'HorizontalBattery'), (r'VisualStateManager', 'VSM'), (r'<test1:', 'test1:'), (r'<svg:', 'svg:'), (r'BitmapCache', 'BitmapCache'), (r'<Grid x:Shared', 'x:Shared')]:
            c = len(re.findall(pat, seg))
            specials.append('%s=%d' % (nm, c))
        io.open(r'D:\doubao space\VioletToolBox\tpl_special.txt', 'w', encoding='utf-8').write('AutorootView ' + ' | '.join(specials) + '\n')
print('done')
