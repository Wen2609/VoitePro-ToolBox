# -*- coding: utf-8 -*-
"""fb_v7 按钮1(读分区表[开机]) 12x"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from PIL import Image
img = Image.open(r'D:\doubao space\VioletToolBox\fb_v7.png')
w, h = img.size
# 按钮1: x 220-385, y 795-850 千分比
bx1, by1 = int(218*w/1000), int(793*h/1000)
bx2, by2 = int(390*w/1000), int(852*h/1000)
crop = img.crop((bx1, by1, bx2, by2))
crop = crop.resize((crop.width*12, crop.height*12), Image.LANCZOS)
crop.save(r'D:\doubao space\VioletToolBox\v7_btn1.png')
print(f'v7_btn1 -> {crop.size}')
# 按钮3: x 578-700, y 795-850
bx1, by1 = int(576*w/1000), int(793*h/1000)
bx2, by2 = int(702*w/1000), int(852*h/1000)
crop2 = img.crop((bx1, by1, bx2, by2))
crop2 = crop2.resize((crop2.width*12, crop2.height*12), Image.LANCZOS)
crop2.save(r'D:\doubao space\VioletToolBox\v7_btn3.png')
print(f'v7_btn3 -> {crop2.size}')
