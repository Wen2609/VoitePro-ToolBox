# -*- coding: utf-8 -*-
import io, re, sys
sys.stdout.reconfigure(encoding='utf-8')
x = io.open(r'D:\doubao space\VioletToolBox\VioletToolBox\MainWindow.xaml', 'r', encoding='utf-8').read()
print('=== StaticResource DropShadowEffect refs ===')
for m in re.finditer(r'.{100}DropShadowEffect.{100}', x):
    print('...', m.group(0).replace('\n', ' '), '...')
print('\n=== Effect= refs ===')
for m in re.finditer(r'.{60}Effect="\{StaticResource[^"]*".{40}', x):
    print('...', m.group(0).replace('\n', ' '), '...')
print('\n=== CornerRadius top-level (Window style) ===')
for m in re.finditer(r'.{100}CornerRadius="[^"]*"', x):
    g = m.group(0)
    if 'Window' in g or 'Border' in g[:120]:
        print('...', g.replace('\n', ' '), '...')
