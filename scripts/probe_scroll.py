# -*- coding: utf-8 -*-
import io, re, sys
sys.stdout.reconfigure(encoding='utf-8')
x = io.open(r'D:\doubao space\VioletToolBox\VioletToolBox\MainWindow.xaml', 'r', encoding='utf-8').read()
for m in re.finditer(r'<DataTemplate x:Key="(Page_\w+)">', x):
    key = m.group(1)
    i = m.end()
    # 配对找模板结束
    depth = 0; j = i
    while j < len(x):
        o = x.find('<DataTemplate', j); c = x.find('</DataTemplate>', j)
        if o == -1 and c == -1: break
        if o != -1 and (c == -1 or o < c): depth += 1; j = o + 13
        else:
            depth -= 1; j = c + 14
            if depth == 0: break
    seg = x[i:j]
    sv = len(re.findall(r'<ScrollViewer', seg))
    h_auto = 'Height="Auto"' in seg
    va = re.search(r'VerticalAlignment="(Top|Stretch)"', seg)
    print(key, '| ScrollViewer:', sv, '| VA:', va.group(1) if va else '?')
