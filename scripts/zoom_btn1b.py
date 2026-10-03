# -*- coding: utf-8 -*-
"""裁剪按钮1（读分区表[开机]）放大 12x"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from PIL import Image
img = Image.open(r'D:\doubao space\VioletToolBox\fb_fixed3.png')
w, h = img.size
# 按钮1区域：x 205-360, y 788-845 千分比（含按钮边框）
bx1, by1 = int(200*w/1000), int(783*h/1000)
bx2, by2 = int(365*w/1000), int(850*h/1000)
crop = img.crop((bx1, by1, bx2, by2))
crop = crop.resize((crop.width*12, crop.height*12), Image.LANCZOS)
crop.save(r'D:\doubao space\VioletToolBox\btn1_12x.png')
print(f'btn1_12x: ({bx1},{by1})-({bx2},{by2}) -> {crop.size}')
