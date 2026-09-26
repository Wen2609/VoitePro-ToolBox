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
        # Grid.Resources 里的样式定义
        styles = re.findall(r'<Style[^>]*x:Key="(Autoroot[A-Za-z]+)"[^>]*>(.*?)</Style>', seg, re.S)
        for skey, body in styles:
            tpl = 'ControlTemplate' in body
            basedon = re.search(r'BasedOn="\{StaticResource ([^}]+)\}"', body)
            setters = re.findall(r'<Setter Property="([^"]+)"', body)
            refs = re.findall(r'\{StaticResource ([^}]+)\}', body)
            out.append('Style %s: tpl=%s basedon=%s setters=%s refs=%s' % (skey, tpl, basedon.group(1) if basedon else '-', setters[:8], refs[:8]))
        # 控件实例引用这些样式
        use = re.findall(r'Style="\{StaticResource (Autoroot[A-Za-z]+)\}"', seg)
        from collections import Counter
        out.append('usage=' + str(Counter(use)))
        io.open(r'D:\doubao space\VioletToolBox\autoroot_styles.txt', 'w', encoding='utf-8').write('\n'.join(out))
        print('done')
