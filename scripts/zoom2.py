# -*- coding: utf-8 -*-
"""裁剪侧边栏 + 更多可疑区域放大"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from PIL import Image

def crop_zoom(src, dst, x1, y1, x2, y2, scale=3):
    img = Image.open(src)
    w, h = img.size
    bx1, by1 = int(x1*w/1000), int(y1*h/1000)
    bx2, by2 = int(x2*w/1000), int(y2*h/1000)
    crop = img.crop((bx1, by1, bx2, by2))
    crop = crop.resize((crop.width*scale, crop.height*scale), Image.LANCZOS)
    crop.save(dst)
    print(f'{dst}: ({bx1},{by1})-({bx2},{by2}) -> {crop.size}')

base = r'D:\doubao space\VioletToolBox\pages_v4'
# 1. 侧边栏全区域（6_hidden 全展开态）
crop_zoom(base + r'\6_hidden.png', r'D:\doubao space\VioletToolBox\zoom_sidebar.png',
          0, 60, 200, 950, 2)
# 2. 欧加线刷 操作区 Top Row（清除数据..修复FastbootD）
crop_zoom(base + r'\3_oujia.png', r'D:\doubao space\VioletToolBox\zoom_oujia_top.png',
          200, 885, 720, 940, 3)
# 3. 可视刷写 操作按钮区
crop_zoom(base + r'\2_fastboot.png', r'D:\doubao space\VioletToolBox\zoom_fb_ops.png',
          190, 755, 650, 880, 3)
# 4. 文件传输 顶部按钮行
crop_zoom(base + r'\7_systemzone.png', r'D:\doubao space\VioletToolBox\zoom_sz_top.png',
          200, 185, 950, 250, 3)
# 5. Rom专区 顶部下载区
crop_zoom(base + r'\13_rom.png', r'D:\doubao space\VioletToolBox\zoom_rom_top.png',
          200, 160, 960, 320, 3)
