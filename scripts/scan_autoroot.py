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
        out.append('AUTOROOT SEG LINES %d-%d' % (x[:pos].count('\n') + 1, x[:end].count('\n') + 1))
        # 可疑模式扫描
        pats = {
            'Style=...DynamicResource': r'Style="\{DynamicResource [^"]+"',
            'StaticResource 引用': r'\{StaticResource [^}]+\}',
            'Binding 无路径': r'Binding="\{Binding [^}]*?"',
            '自定义命名空间': r'xmlns:\w+="clr-namespace',
            '附加属性 hc:': r'\bhc:[A-Za-z]',
            '附加属性 自定义': r'\b(?:d|local|test1):[A-Za-z]',
            'x:Static': r'\{x:Static [^}]+\}',
            'Image Source': r'<Image[^>]*Source=',
            'SvgImage': r'<svg:',
        }
        for nm, pat in pats.items():
            c = len(re.findall(pat, seg))
            if c: out.append('  %s: %d' % (nm, c))
        # 第一层结构（模板根的命名空间）
        m = re.search(r'<DataTemplate[^>]*>(.{0,600})', seg, re.S)
        if m: out.append('  ROOT: ' + m.group(1).replace('\n', ' ')[:400])
io.open(r'D:\doubao space\VioletToolBox\autoroot_scan.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('done')
