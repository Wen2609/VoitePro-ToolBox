# -*- coding: utf-8 -*-
import io, re, sys
sys.stdout.reconfigure(encoding='utf-8')
x = io.open(r'D:\doubao space\VioletToolBox\VioletToolBox\MainWindow.xaml', 'r', encoding='utf-8').read()
# 找所有 Page_AutorootView 定义
for m in re.finditer(r'<DataTemplate\s+x:Key="Page_AutorootView"', x):
    print('def at L%d (line %d)' % (m.start(), x[:m.start()].count('\n') + 1))
# 找第一个嵌套的内部模板（在外部模板段内）
outer = re.search(r'<DataTemplate\s+x:Key="Page_AutorootView">', x)
if outer:
    ostart = outer.start()
    # 找段内第二个同名定义
    inner = re.search(r'<DataTemplate\s+x:Key="Page_AutorootView">', x[ostart+1:])
    if inner:
        ipos = ostart + 1 + inner.start()
        line = x[:ipos].count('\n') + 1
        print('NESTED def at L%d' % line)
        # 打印嵌套定义周围
        ctx = x[max(0, ipos-600):ipos+300]
        print('--- context ---')
        print(ctx)
