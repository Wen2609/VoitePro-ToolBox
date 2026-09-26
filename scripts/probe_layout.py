# -*- coding: utf-8 -*-
import io, sys, re
sys.stdout.reconfigure(encoding='utf-8')
x = io.open(r'D:\doubao space\VioletToolBox\VioletToolBox\MainWindow.xaml', 'r', encoding='utf-8').read()
# PageHost 容器结构
ph = x.find('x:Name="PageHost"')
print('=== PageHost ctx ===')
print(x[ph-1600:ph+150].replace('\n', ' ')[:1800])
print()
# 所有模板根 Grid（Page_ 模板第一个 Grid）
print('=== template root Grid attrs ===')
for m in re.finditer(r'<DataTemplate x:Key="(Page_\w+)">(.*?)<Grid\s([^>]*)>', x, re.S):
    key = m.group(1)
    attrs = m.group(3)
    w = re.search(r'Width="([^"]*)"', attrs)
    h = re.search(r'Height="([^"]*)"', attrs)
    ha = re.search(r'HorizontalAlignment="([^"]*)"', attrs)
    va = re.search(r'VerticalAlignment="([^"]*)"', attrs)
    flags = []
    if w: flags.append('W=' + w.group(1))
    if h: flags.append('H=' + h.group(1))
    if ha and ha.group(1) != 'Stretch': flags.append('HA=' + ha.group(1))
    if va and va.group(1) != 'Stretch': flags.append('VA=' + va.group(1))
    if re.search(r'Width="[0-9]', attrs): flags.append('FIXED_W!')
    print(key, '->', ' '.join(flags) if flags else '(clean Stretch)')
