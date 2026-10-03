# -*- coding: utf-8 -*-
"""fb_v7 操作区 5x 逐按钮目测"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from PIL import Image
img = Image.open(r'D:\doubao space\VioletToolBox\fb_v7.png')
w, h = img.size
bx1, by1 = int(185*w/1000), int(745*h/1000)
bx2, by2 = int(825*w/1000), int(895*h/1000)
crop = img.crop((bx1, by1, bx2, by2))
crop = crop.resize((crop.width*5, crop.height*5), Image.LANCZOS)
crop.save(r'D:\doubao space\VioletToolBox\fb_v7_ops.png')
print(f'fb_v7_ops -> {crop.size}')
