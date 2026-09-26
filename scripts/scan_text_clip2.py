# -*- coding: utf-8 -*-
"""扫描 Content 文字长度 vs Width 的按钮，找可能裁切的"""
import io, re, sys
sys.stdout.reconfigure(encoding='utf-8')
p = r'D:\doubao space\VioletToolBox\VioletToolBox\MainWindow.xaml'
c = io.open(p, 'r', encoding='utf-8').read()

# 按元素块解析：<Button ... Content="X" ... Width="N">
# 简单：逐行找 Content= 和 Width=
lines = c.split('\n')
print('=== 单行 Button: Content 中文长度 >= 6 且 Width <= 130 ===')
for i, ln in enumerate(lines, 1):
    if '<Button' not in ln: continue
    cm = re.search(r'Content="([^"]+)"', ln)
    wm = re.search(r'Width="(\d+)"', ln)
    if not cm or not wm: continue
    text = cm.group(1)
    width = int(wm.group(1))
    # 估算：中文 14px/字 + 内边距 20
    cjk = len(re.findall(r'[\u4e00-\u9fff]', text))
    other = len(text) - cjk
    est = cjk * 14 + other * 8 + 20
    if cjk >= 5 and est > width:
        print(f'L{i}: "{text}" Width={width} est≈{est}px 可能裁切')

# 多行 Button（Content 在下一行）
print('\n=== 多行 Button: Content 中文长度 >= 6 且 Width <= 130 ===')
for i, ln in enumerate(lines, 1):
    if '<Button' not in ln or 'Content' not in ln: continue
    # Content 与 Width 同行或多行——用正则跨行
    pass
# 跨行解析：找 Button 块（到 /> 或 </Button>）
block_pat = re.compile(r'<Button\b[^>]*?(?:Content="([^"]+)"[^>]*?Width="(\d+)"|Width="(\d+)"[^>]*?Content="([^"]+)")', re.S)
for m in block_pat.finditer(c):
    text = m.group(1) or m.group(4)
    width = int(m.group(2) or m.group(3))
    if text is None or width is None: continue
    cjk = len(re.findall(r'[\u4e00-\u9fff]', text))
    other = len(text) - cjk
    est = cjk * 14 + other * 8 + 20
    if cjk >= 5 and est > width:
        # 定位行号
        ln = c[:m.start()].count('\n') + 1
        print(f'L{ln}: "{text}" Width={width} est≈{est}px 可能裁切')
