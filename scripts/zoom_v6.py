# -*- coding: utf-8 -*-
"""fb_v6 操作区 4x 目测单行按钮"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from PIL import Image
img = Image.open(r'D:\doubao space\VioletToolBox\fb_v6.png')
w, h = img.size
bx1, by1 = int(190*w/1000), int(770*h/1000)
bx2, by2 = int(760*w/1000), int(900*h/1000)
crop = img.crop((bx1, by1, bx2, by2))
crop = crop.resize((crop.width*4, crop.height*4), Image.LANCZOS)
crop.save(r'D:\doubao space\VioletToolBox\fb_v6_ops.png')
print(f'fb_v6_ops -> {crop.size}')
