# -*- coding: utf-8 -*-
"""fb_v9 操作区 4x"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from PIL import Image
img = Image.open(r'D:\doubao space\VioletToolBox\fb_v9.png')
w, h = img.size
bx1, by1 = int(185*w/1000), int(745*h/1000)
bx2, by2 = int(825*w/1000), int(895*h/1000)
crop = img.crop((bx1, by1, bx2, by2))
crop = crop.resize((crop.width*4, crop.height*4), Image.LANCZOS)
crop.save(r'D:\doubao space\VioletToolBox\fb_v9_ops.png')
print(f'fb_v9_ops -> {crop.size}')
