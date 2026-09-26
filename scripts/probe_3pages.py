# -*- coding: utf-8 -*-
import io, re, sys
sys.stdout.reconfigure(encoding='utf-8')
x = io.open(r'D:\doubao space\VioletToolBox\VioletToolBox\MainWindow.xaml', 'r', encoding='utf-8').read()
for key in ['Page_PayloadView', 'Page_RomDownloadview', 'Page_ColorOSAssistantView']:
    m = re.search(r'<DataTemplate x:Key="' + key + r'">', x)
    i = m.end()
    # 根 Grid
    rm = re.search(r'<Grid\s+Name="' + key.replace('Page_', '') + r'"', x[i:])
    gi = i + rm.start()
    gt = x.find('>', gi)
    print('===', key, '===')
    print('root attrs:', x[gi:gt+1].replace('\n', ' ')[:250])
    # 属性元素检查
    seg = x[gt+1:gt+800]
    has_res = '<Grid.Resources>' in seg
    has_row = '<Grid.RowDefinitions>' in seg
    has_col = '<Grid.ColumnDefinitions>' in seg
    print('Resources:', has_res, '| RowDefs:', has_row, '| ColDefs:', has_col)
    # 前 300 内容
    print('content head:', x[gt+1:gt+301].replace('\n', ' ')[:300])
    print()
