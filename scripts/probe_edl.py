# -*- coding: utf-8 -*-
import io, re, sys
sys.stdout.reconfigure(encoding='utf-8')
x = io.open(r'D:\doubao space\VioletToolBox\VioletToolBox\MainWindow.xaml', 'r', encoding='utf-8').read()
# EdlFlashView 模板范围
i = x.find('x:Key="Page_EdlFlashView"')
if i == -1:
    print('Page_EdlFlashView NOT FOUND')
else:
    # 找模板结束（</DataTemplate>）
    j = x.find('</DataTemplate>', i)
    print('EdlFlashView template length:', j - i)
    print('=== head ===')
    print(x[i:i+1500])
