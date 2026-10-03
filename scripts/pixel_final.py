# -*- coding: utf-8 -*-
"""最终检测：排除按钮边框后文字右缘"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from PIL import Image

img = Image.open(r'D:\doubao space\VioletToolBox\fb_fixed3.png').convert('L')
w, h = img.size

# 列（按钮1: 210-356, 按钮2: 364-511）排除边框 2px
cols = [(214, 352, '读分区表[开机]'), (368, 506, '读分区表[FB]')]
for x0, x1, label in cols:
    dark = []
    for x in range(x0, x1):
        for y in range(674, 715):  # 避开上下边框
            if img.getpixel((x, y)) < 100:
                dark.append(x)
                break
    if not dark:
        print(f'{label}: no text')
        continue
    xmin, xmax = dark[0], dark[-1]
    span = xmax - xmin + 1
    right_room = x1 - 1 - xmax
    print(f'{label}: text {xmin}-{xmax} span{span}px, right room in btn {right_room}px -> {"FULL" if right_room >= 3 else ("TIGHT" if right_room >= 0 else "CLIP")}')
