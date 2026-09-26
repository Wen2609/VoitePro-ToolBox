# -*- coding: utf-8 -*-
"""裁剪放大可疑区域，目测文字裁切/遮挡"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
try:
    from PIL import Image
except ImportError:
    import subprocess
    subprocess.run([sys.executable, '-m', 'pip', 'install', 'Pillow', '-q'])
    from PIL import Image

def crop_zoom(src, dst, x1, y1, x2, y2, scale=3):
    img = Image.open(src)
    w, h = img.size
    # 千分比 → 像素
    bx1, by1 = int(x1*w/1000), int(y1*h/1000)
    bx2, by2 = int(x2*w/1000), int(y2*h/1000)
    crop = img.crop((bx1, by1, bx2, by2))
    crop = crop.resize((crop.width*scale, crop.height*scale), Image.LANCZOS)
    crop.save(dst)
    print(f'{dst}: crop ({bx1},{by1})-({bx2},{by2}) -> {crop.size}')

base = r'D:\doubao space\VioletToolBox\pages_v4'
# 1. 欧加线刷 "修复Super真死" 按钮（含下方初始化遮罩对比）
crop_zoom(base + r'\3_oujia.png', r'D:\doubao space\VioletToolBox\zoom_oujia_fix.png',
          540, 425, 700, 480, 4)
# 2. 欧加操作区按钮行
crop_zoom(base + r'\3_oujia.png', r'D:\doubao space\VioletToolBox\zoom_oujia_ops.png',
          200, 880, 720, 1000, 3)
# 3. 隐藏ROOT 操作按钮区
crop_zoom(base + r'\6_hidden.png', r'D:\doubao space\VioletToolBox\zoom_hidden_ops.png',
          220, 350, 540, 420, 4)
# 4. 基本刷入 扩展功能按钮
crop_zoom(base + r'\1_basic.png', r'D:\doubao space\VioletToolBox\zoom_basic_ext.png',
          630, 430, 980, 640, 3)
# 5. 降级助手 第二步/第三步按钮区（用户当前看的页）
crop_zoom(r'D:\doubao space\VioletToolBox\cur_state.png', r'D:\doubao space\VioletToolBox\zoom_coloros_steps.png',
          200, 230, 500, 420, 4)
