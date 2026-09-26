# -*- coding: utf-8 -*-
import io, re, sys, xml.parsers.expat
sys.stdout.reconfigure(encoding='utf-8')
fp = r'D:\doubao space\VioletToolBox\VioletToolBox\MainWindow.xaml'
x = io.open(fp, 'r', encoding='utf-8').read()
# 1) 结构计数
print('PageHost:', x.count('x:Name="PageHost"'))
print('DataTemplate Page_ count:', len(re.findall(r'<DataTemplate x:Key="Page_', x)))
print('DownloadView:', x.count('Name="DownloadView"'))
for name in ['DriverTileView','DriverListView','DriverFileListBox','DriverLoadingView']:
    print(name, 'x:Name count:', x.count('x:Name="'+name+'"'))
# 2) XML 良构
ok = True
try:
    p = xml.parsers.expat.ParserCreate()
    p.Parse(x, True)
    print('XML well-formed: True')
except Exception as e:
    ok = False
    print('XML well-formed: False:', e)
