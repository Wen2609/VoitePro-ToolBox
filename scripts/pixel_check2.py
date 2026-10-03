# -*- coding: utf-8 -*-
"""像素级检测按钮文字（纯 PIL）"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from PIL import Image

img = Image.open(r'D:\doubao space\VioletToolBox\fb_fixed2.png').convert('L')
w, h = img.size
print(f'img {w}x{h}')

# 按钮行区域 y 671-718, x 202-747（与放大裁剪一致）
# 4 按钮均分
btn_w = (747-202)//4  # 136
for i in range(4):
    x0 = 202 + i*btn_w
    x1 = x0 + btn_w
    dark_min_x = None
    dark_max_x = None
    for x in range(x0, x1):
        has_dark = False
        for y in range(671, 718):
            if img.getpixel((x, y)) < 128:
                has_dark = True
                break
        if has_dark:
            if dark_min_x is None: dark_min_x = x
            dark_max_x = x
    if dark_min_x is None:
        print(f'btn{i+1}: no dark text')
        continue
    gap_r = x1 - 1 - dark_max_x
    gap_l = dark_min_x - x0
    print(f'btn{i+1}: text x {dark_min_x}-{dark_max_x} (btn {x0}-{x1}), left gap {gap_l}px, right gap {gap_r}px {"<< CLIPPED" if gap_r <= 4 else ""}')
