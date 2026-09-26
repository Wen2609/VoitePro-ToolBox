# -*- coding: utf-8 -*-
import io, re, sys
sys.stdout.reconfigure(encoding='utf-8')
x = io.open(r'D:\doubao space\VioletToolBox\VioletToolBox\MainWindow.xaml', 'r', encoding='utf-8').read()
for key in ['Page_RomDownloadview', 'Page_ColorOSAssistantView']:
    m = re.search(r'<DataTemplate x:Key="' + key + r'">', x)
    if not m:
        print(key, 'NOT FOUND'); continue
    seg = x[m.end():m.end()+3000]
    root = re.search(r'<Grid\s+Name="([^"]+)"', seg)
    print('===', key, 'root Grid Name:', root.group(1) if root else '?')
    # 找 Grid.Row="1" Grid 和 RowDefinitions
    rows = re.findall(r'<Grid\s+Grid\.Row="(\d+)"[^>]*>', seg)
    print('Grid.Row occurrences in first 3000:', rows[:5])
    has_scroll = '<ScrollViewer' in seg
    print('has ScrollViewer in first 3000:', has_scroll)
    # RowDefinitions
    rd = re.search(r'<Grid.RowDefinitions>\s*<RowDefinition[^>]*Height="([^"]*)"', seg)
    print('first RowDef:', rd.group(1) if rd else 'none')
