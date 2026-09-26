# -*- coding: utf-8 -*-
import io, re, sys
sys.stdout.reconfigure(encoding='utf-8')
x = io.open(r'D:\doubao space\VioletToolBox\VioletToolBox\MainWindow.xaml', 'r', encoding='utf-8').read()
for m in re.finditer(r'<DataTemplate[^>]*x:Key="Page_AutorootView"', x):
    print('key=Page_AutorootView at L%d' % (x[:m.start()].count('\n') + 1))
    print('   ctx:', x[m.start():m.start()+200].replace('\n', ' ')[:180])
# 也找 x:Key 里有 Autoroot 的其他模板
for m in re.finditer(r'<DataTemplate[^>]*x:Key="([^"]*Autoroot[^"]*)"', x):
    print('Autoroot-tpl at L%d key=%s' % (x[:m.start()].count('\n') + 1, m.group(1)))
