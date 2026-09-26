# -*- coding: utf-8 -*-
import io, re, sys
sys.stdout.reconfigure(encoding='utf-8')
x = io.open(r'D:\doubao space\VioletToolBox\VioletToolBox\MainWindow.xaml', 'r', encoding='utf-8').read()
# 窗口头部 1500 字符
print('=== Window head ===')
print(x[:1600])
# Effect 出现
print('\n=== Effect occurrences ===')
for m in re.finditer(r'.{80}Effect.{80}', x):
    print('...', m.group(0).replace('\n', ' '), '...')
