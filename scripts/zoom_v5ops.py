# -*- coding: utf-8 -*-
"""fb_v5 操作区整行（含两行按钮）8x"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from PIL import Image
img = Image.open(r'D:\doubao space\VioletToolBox\fb_v5.png')
w, h = img.size
bx1, by1 = int(190*w/1000), int(770*h/1000)
bx2, by2 = int(760*w/1000), int(890*h/1000)
crop = img.crop((bx1, by1, bx2, by2))
crop = crop.resize((crop.width*8, crop.height*8), Image.LANCZOS)
crop.save(r'D:\doubao space\VioletToolBox\fb_v5_ops.png')
print(f'fb_v5_ops -> {crop.size}')
