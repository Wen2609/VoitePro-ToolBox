# -*- coding: utf-8 -*-
"""放大 fb_fixed 按钮行目测"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from PIL import Image
src = r'D:\doubao space\VioletToolBox\fb_fixed.png'
img = Image.open(src)
w, h = img.size
# 读分区表按钮行（原图 220-800, 800-830 千分比）
bx1, by1 = int(200*w/1000), int(790*h/1000)
bx2, by2 = int(740*w/1000), int(845*h/1000)
crop = img.crop((bx1, by1, bx2, by2))
crop = crop.resize((crop.width*4, crop.height*4), Image.LANCZOS)
crop.save(r'D:\doubao space\VioletToolBox\fb_btnrow.png')
print(f'fb_btnrow: ({bx1},{by1})-({bx2},{by2}) -> {crop.size}')
