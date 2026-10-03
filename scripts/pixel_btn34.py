# -*- coding: utf-8 -*-
"""检测 fb_v6 按钮3/4 文字右缘"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from PIL import Image
img = Image.open(r'D:\doubao space\VioletToolBox\fb_v6.png').convert('L')
w, h = img.size
# 按钮行 y 800-850 千分比
# 按钮3 预计 x 545-680（列4），按钮4 预计 x 688-823（列6）
for label, x0, x1 in [('写入分区', 545, 680), ('擦除分区', 688, 823)]:
    dark = []
    for x in range(x0, x1):
        for y in range(int(0.808*h), int(0.845*h)):
            if img.getpixel((x, y)) < 100:
                dark.append(x)
                break
    if not dark:
        print(f'{label}: no text in {x0}-{x1}')
        continue
    xmin, xmax = dark[0], dark[-1]
    print(f'{label}: text {xmin}-{xmax} span{xmax-xmin+1}px, right edge {x1-1-xmax}px away from {x1}')
# 按钮1 参考
dark1 = []
for x in range(213, 372):
    for y in range(int(0.808*h), int(0.845*h)):
        if img.getpixel((x, y)) < 100:
            dark1.append(x)
            break
print(f'读分区表[开机]: text {dark1[0]}-{dark1[-1]} span{dark1[-1]-dark1[0]+1}px')
