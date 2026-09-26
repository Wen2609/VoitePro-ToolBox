# -*- coding: utf-8 -*-
import io, sys
sys.stdout.reconfigure(encoding='utf-8')
x = io.open(r'D:\doubao space\VioletToolBox\VioletToolBox\MainWindow.xaml', 'r', encoding='utf-8').read()
i = x.find('Name="HomeView"')
# 侧边栏在 HomeView 前（同 Grid.Column=0）
seg = x[i-6500:i]
print('=== sidebar region (6000 chars before HomeView) ===')
print(seg[:6000])
