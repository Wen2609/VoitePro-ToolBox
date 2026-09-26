# -*- coding: utf-8 -*-
import io, re, sys
sys.stdout.reconfigure(encoding='utf-8')
x = io.open(r'D:\doubao space\VioletToolBox\VioletToolBox\MainWindow.xaml', 'r', encoding='utf-8').read()
i = x.find('x:Key="Page_BasicFlashView"')
j = x.find('</DataTemplate>', i)
seg = x[i:j]
# 扩展功能区域：查 "扩展功能" 上下文
k = seg.find('扩展功能')
print('=== 扩展功能 region ===')
print(seg[k-400:k+2600])
