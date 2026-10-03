# -*- coding: utf-8 -*-
"""放大 fb_fixed2 按钮行 6x 目测"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from PIL import Image
img = Image.open(r'D:\doubao space\VioletToolBox\fb_fixed2.png')
w, h = img.size
# 读分区表按钮行（原图 x 200-750, y 790-845 千分比）
bx1, by1 = int(190*w/1000), int(785*h/1000)
bx2, by2 = int(760*w/1000), int(850*h/1000)
crop = img.crop((bx1, by1, bx2, by2))
crop = crop.resize((crop.width*6, crop.height*6), Image.LANCZOS)
crop.save(r'D:\doubao space\VioletToolBox\fb_btnrow2.png')
print(f'fb_btnrow2: ({bx1},{by1})-({bx2},{by2}) -> {crop.size}')
