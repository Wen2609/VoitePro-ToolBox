# -*- coding: utf-8 -*-
import io, re, sys
sys.stdout.reconfigure(encoding='utf-8')
x = io.open(r'D:\doubao space\VioletToolBox\VioletToolBox\MainWindow.xaml', 'r', encoding='utf-8').read()
m = re.search(r'<DataTemplate x:Key="Page_SystemZoneView">', x)
print('template at', m.start())
te_marker = x.find('<DataTemplate.Resources>', m.end())
print('first DataTemplate.Resources at', te_marker - m.end(), 'chars in')
# 根 Grid
rm = re.search(r'<Grid\s+Name="SystemZoneView"', x[m.end():])
gi = m.end() + rm.start()
gt = x.find('>', gi)
print('root Grid open ends at', gt - gi, 'chars in')
seg = x[gi:gt]
print('root grid attrs:', seg[:300])
print()
print('=== next 1000 chars after root grid open ===')
print(x[gt+1:gt+1001])
