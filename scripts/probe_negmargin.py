# -*- coding: utf-8 -*-
import io, sys, re
sys.stdout.reconfigure(encoding='utf-8')
x = io.open(r'D:\doubao space\VioletToolBox\VioletToolBox\MainWindow.xaml', 'r', encoding='utf-8').read()
# 全部负 Margin 上下文（判断严重性）
count = 0
for m in re.finditer(r'Margin="[^"]*-[0-9][^"]*"', x):
    s = x[max(0,m.start()-130):m.end()+30].replace('\n', ' ')
    s = re.sub(r'\s+', ' ', s)
    print(count+1, ':', s[:220])
    count += 1
    if count >= 47: break
print('total shown:', count)
