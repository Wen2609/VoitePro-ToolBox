# -*- coding: utf-8 -*-
"""精确检测按钮文字右缘（深蓝<100）vs 按钮边界"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from PIL import Image

img = Image.open(r'D:\doubao space\VioletToolBox\fb_fixed2.png').convert('L')
w, h = img.size
print(f'img {w}x{h}')

# 操作区 GroupBox 内容起点：x≈210（窗口 1010 千分比 208）
# 4 Star 列：146.5 + 8 间隔。按钮1 列 210-356，按钮2 列 364.5-511
# 行：y 671-718（读分区表行，之前裁剪）
col_starts = [210, 364.5, 519, 673.5]
col_ends = [356.5, 511, 665.5, 820]
labels = ['读分区表[开机]', '读分区表[FB]', '写入分区', '擦除分区']
for i in range(4):
    x0, x1 = int(col_starts[i]), int(col_ends[i])
    dark = []
    for x in range(x0, x1):
        for y in range(671, 718):
            if img.getpixel((x, y)) < 100:  # 深蓝文字
                dark.append(x)
                break
    if not dark:
        print(f'{labels[i]}: no dark text in col')
        continue
    xmin, xmax = dark[0], dark[-1]
    right_gap = x1 - 1 - xmax
    left_gap = xmin - x0
    status = 'OK' if right_gap >= 6 else ('TIGHT' if right_gap >= 0 else 'OVERFLOW')
    print(f'{labels[i]}: text {xmin}-{xmax} col {x0}-{x1} Lgap{left_gap} Rgap{right_gap} -> {status}')
