# -*- coding: utf-8 -*-
"""fb_v4 按钮1 右半（机]区域）20x 目测"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from PIL import Image
img = Image.open(r'D:\doubao space\VioletToolBox\fb_v4.png')
w, h = img.size
# 按钮1右半：x 280-368, y 780-860 千分比
bx1, by1 = int(275*w/1000), int(775*h/1000)
bx2, by2 = int(372*w/1000), int(865*h/1000)
crop = img.crop((bx1, by1, bx2, by2))
crop = crop.resize((crop.width*20, crop.height*20), Image.LANCZOS)
crop.save(r'D:\doubao space\VioletToolBox\btn1_right.png')
print(f'btn1_right -> {crop.size}')
