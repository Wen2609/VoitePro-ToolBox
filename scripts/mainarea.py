# -*- coding: utf-8 -*-
import io, sys
sys.stdout.reconfigure(encoding='utf-8')
x = io.open(r'D:\doubao space\VioletToolBox\VioletToolBox\MainWindow.xaml', 'r', encoding='utf-8').read()
# HomeView L9431 附近结构
idx = x.find('Name="HomeView"')
print('=== HomeView ctx ===')
print(x[idx-700:idx+500].replace('\n', ' ')[:1200])
# PageHost L9959 前 500
ph = x.find('x:Name="PageHost"')
print('\n=== PageHost ctx ===')
print(x[ph-800:ph+200].replace('\n', ' ')[:1000])
