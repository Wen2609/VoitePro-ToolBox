# -*- coding: utf-8 -*-
"""用户截图按钮行 4x"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from PIL import Image
img = Image.open(r'C:\Users\Administrator\AppData\Local\Packages\MicrosoftWindows.Client.Core_cw5n1h2txyewy\TempState\ScreenClip\{ED842914-F92A-4D93-A9FA-A6D658031A41}.png')
w, h = img.size
print(f'user img {w}x{h}')
# 按钮行（读分区表两行区域）：x 40-860, y 840-930 千分比
bx1, by1 = int(40*w/1000), int(835*h/1000)
bx2, by2 = int(870*w/1000), int(935*h/1000)
crop = img.crop((bx1, by1, bx2, by2))
crop = crop.resize((crop.width*4, crop.height*4), Image.LANCZOS)
crop.save(r'D:\doubao space\VioletToolBox\user_btnrow.png')
print(f'user_btnrow -> {crop.size}')
