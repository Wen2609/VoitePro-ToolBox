# -*- coding: utf-8 -*-
import io, sys, re
sys.stdout.reconfigure(encoding='utf-8')
x = io.open(r'D:\doubao space\VioletToolBox\VioletToolBox\MainWindow.xaml', 'r', encoding='utf-8').read()
print('=== negative Margin count ===')
print(len(re.findall(r'Margin="[^"]*-[0-9]', x)))
print('=== Canvas absolute ===')
print(len(re.findall(r'<Canvas', x)))
print('=== fixed-width TextBlock (Width="[0-9] with Text=) ===')
tb = re.findall(r'<TextBlock[^>]*Width="([0-9]+)"[^>]*>', x)
print('TextBlock fixed width count:', len(tb), 'sample:', tb[:10])
print('=== Button fixed width ===')
bt = re.findall(r'<Button[^>]*Width="([0-9]+)"', x)
print('Button fixed width count:', len(bt))
print('=== Grid fixed Height rows/cols (Height="[0-9]) ===')
gh = re.findall(r'<Grid[^>]*Height="([0-9]+)"', x)
print('Grid fixed height count:', len(gh))
print('=== StackPanel fixed width ===')
sp = re.findall(r'<StackPanel[^>]*Width="([0-9]+)"', x)
print('StackPanel fixed width count:', len(sp))
# 负 margin 上下文样例
print('=== negative margin samples ===')
for m in re.finditer(r'.{70}Margin="[^"]*-[0-9].{70}', x)[:0] if False else []:
    pass
i = 0
for m in re.finditer(r'Margin="[^"]*-[0-9][^"]*"', x):
    s = x[max(0,m.start()-90):m.end()+20].replace('\n',' ')
    print('---', s[:180])
    i += 1
    if i >= 12: break
