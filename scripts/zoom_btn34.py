# -*- coding: utf-8 -*-
"""fb_v6 按钮3/4 区域 6x"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from PIL import Image
img = Image.open(r'D:\doubao space\VioletToolBox\fb_v6.png')
w, h = img.size
bx1, by1 = int(530*w/1000), int(795*h/1000)
bx2, by2 = int(700*w/1000), int(855*h/1000)
crop = img.crop((bx1, by1, bx2, by2))
crop = crop.resize((crop.width*6, crop.height*6), Image.LANCZOS)
crop.save(r'D:\doubao space\VioletToolBox\btn34_6x.png')
print(f'btn34_6x -> {crop.size}')
