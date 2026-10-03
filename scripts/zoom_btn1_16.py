# -*- coding: utf-8 -*-
"""fb_final 按钮1 16x 目测"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from PIL import Image
img = Image.open(r'D:\doubao space\VioletToolBox\fb_final.png')
w, h = img.size
bx1, by1 = int(198*w/1000), int(780*h/1000)
bx2, by2 = int(368*w/1000), int(852*h/1000)
crop = img.crop((bx1, by1, bx2, by2))
crop = crop.resize((crop.width*16, crop.height*16), Image.LANCZOS)
crop.save(r'D:\doubao space\VioletToolBox\btn1_16x.png')
print(f'btn1_16x -> {crop.size}')
