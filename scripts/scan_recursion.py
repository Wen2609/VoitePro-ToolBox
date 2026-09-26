# -*- coding: utf-8 -*-
import io, re, sys
sys.stdout.reconfigure(encoding='utf-8')
x = io.open(r'D:\doubao space\VioletToolBox\VioletToolBox\MainWindow.xaml', 'r', encoding='utf-8').read()
tpls = [(m2.group(1), m2.start()) for m2 in re.finditer(r'<DataTemplate\s+x:Key="(?:DISABLED_)?(Page_[A-Za-z0-9]+)"', x)]
for i, (key, pos) in enumerate(tpls):
    if key == 'Page_AutorootView':
        end = tpls[i+1][1] if i+1 < len(tpls) else len(x)
        seg = x[pos:end]
        out = []
        # 1) 模板内引用模板自身
        for pat, nm in [(r'Page_AutorootView', 'Page_AutorootView自引用'), (r'\bAutorootView\b', 'AutorootView名字'), (r'ContentTemplate', 'ContentTemplate'), (r'ContentControl', 'ContentControl')]:
            c = len(re.findall(pat, seg))
            out.append('%s=%d' % (nm, c))
        # 2) Grid.Resources 里的样式（可能循环）
        rs = re.findall(r'<Style[^>]*x:Key="([^"]+)"[^>]*>', seg)
        out.append('styles=' + ','.join(rs[:20]))
        # 3) 所有 StaticResource 引用
        srs = re.findall(r'\{StaticResource ([^}]+)\}', seg)
        from collections import Counter
        out.append('staticrefs=' + str(Counter(srs).most_common(20)))
        # 4) 找 BasedOn / 继承
        bos = re.findall(r'BasedOn="\{StaticResource ([^}]+)\}"', seg)
        out.append('basedon=' + str(bos))
        # 5) SvgImage 源
        svs = re.findall(r'<svg:SvgImage[^>]*Source="([^"]+)"', seg)
        out.append('svg-sources=' + str(set(svs)))
        # 6) 模板内嵌套 DataTemplate
        ndt = re.findall(r'<DataTemplate[^>]*x:Key="([^"]+)"', seg)
        out.append('nested-tpl=' + str(ndt))
        io.open(r'D:\doubao space\VioletToolBox\autoroot_rec.txt', 'w', encoding='utf-8').write('\n'.join(out))
        print('written')
