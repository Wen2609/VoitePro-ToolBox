# -*- coding: utf-8 -*-
"""扫描按钮4文字位置"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from PIL import Image
img = Image.open(r'D:\doubao space\VioletToolBox\fb_v7.png').convert('L')
w, h = img.size
# 扫描整行 y 805-850 x 200-900 的深色块
runs = []
in_run = False
run_start = 0
for x in range(200, 900):
    has = any(img.getpixel((x, y)) < 100 for y in range(int(0.805*h), int(0.85*h)))
    if has and not in_run:
        in_run = True; run_start = x
    elif not has and in_run:
        in_run = False; runs.append((run_start, x-1))
if in_run: runs.append((run_start, 899))
for r in runs:
    if r[1]-r[0] > 8:
        print(f'block {r[0]}-{r[1]} span{r[1]-r[0]+1}px')
