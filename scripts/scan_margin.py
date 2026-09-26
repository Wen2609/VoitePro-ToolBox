# -*- coding: utf-8 -*-
"""扫描所有大左边距偏移元素（可能盖住同行前元素）"""
import io, re, sys
sys.stdout.reconfigure(encoding='utf-8')
p = r'D:\doubao space\VioletToolBox\VioletToolBox\MainWindow.xaml'
c = io.open(p, 'r', encoding='utf-8').read()

# 找 Margin="N,0,0,0" N>=100 的元素
pat = re.compile(r'<(\w+)([^>]*?)(?:/>|>)', re.S)
lines = c.split('\n')
print('=== Margin.Left >= 100 的元素 ===')
for i, ln in enumerate(lines, 1):
    m = re.search(r'Margin="(\d{2,}),0,0,0"', ln)
    if m and int(m.group(1)) >= 100:
        # 提取元素名和 content
        tag = re.search(r'<(\w+)', ln)
        content = re.search(r'Content="([^"]*)"', ln)
        name = re.search(r'x:Name="([^"]*)"', ln)
        print(f'L{i}: Margin={m.group(1)} tag={tag.group(1) if tag else "?"} '
              f'content={content.group(1) if content else ""} name={name.group(1) if name else ""}')

# 找 Grid 内"StackPanel + 兄弟元素"可能重叠的模式：同一 Grid 有 StackPanel 和带大 Margin 的元素
print('\n=== 大 Margin 元素前 4 行上下文（判断是否盖住） ===')
for i, ln in enumerate(lines, 1):
    m = re.search(r'Margin="(\d{2,}),0,0,0"', ln)
    if m and int(m.group(1)) >= 100:
        start = max(0, i-6)
        print(f'--- L{i} ---')
        for j in range(start, i+1):
            t = lines[j].strip()
            if t and len(t) < 160:
                print(f'  L{j}: {t}')
