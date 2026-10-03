# -*- coding: utf-8 -*-
"""扫描 MainWindow.xaml 中所有固定宽度按钮，估算文字像素宽度，找出文字可能被裁的按钮"""
import io, re, sys
sys.stdout.reconfigure(encoding='utf-8')
x = io.open(r'D:\doubao space\VioletToolBox\VioletToolBox\MainWindow.xaml', 'r', encoding='utf-8').read()

# 估算文字宽度: 中文字符=1.0*fontsize, 拉丁=0.55*fontsize, 数字=0.55
def est_width(text, fs):
    w = 0
    for ch in text:
        if ord(ch) > 0x2E80:  # CJK
            w += 1.0 * fs
        elif ch in 'ilI.,:;|1!':
            w += 0.30 * fs
        else:
            w += 0.55 * fs
    return w

results = []
# 匹配 Button 标签块（含属性），提取 Width、Content、内部 TextBlock、FontSize
pat = re.compile(r'<Button\b[^>]*>', re.S)
for m in pat.finditer(x):
    seg = m.group(0)
    if 'Width=' not in seg:
        continue
    wm = re.search(r'Width="(\d+)"', seg)
    if not wm:
        continue
    width = int(wm.group(1))
    # 文字来源: Content="..." 或内部 <TextBlock Text="..."
    text = ''
    cm = re.search(r'Content="([^"]*)"', seg)
    if cm:
        text = cm.group(1)
    else:
        tm = re.search(r'<TextBlock[^>]*Text="([^"]*)"', seg)
        if tm:
            text = tm.group(1)
    if not text:
        continue
    # FontSize: 属性或默认 12
    fm = re.search(r'FontSize="([\d.]+)"', seg)
    fs = float(fm.group(1)) if fm else 12.0
    need = est_width(text, fs) + 16  # 图标 + padding 余量
    if width < need:
        results.append((m.start(), width, round(need), fs, text[:28], seg[:160].replace('\n',' ')))

print(f"total buttons with width+text: {len([1 for m in pat.finditer(x) if 'Width=' in m.group(0) and ('Content=' in m.group(0) or '<TextBlock' in m.group(0))])}")
print(f"overflow candidates: {len(results)}")
for ln, w, need, fs, t, ctx in sorted(results, key=lambda r: r[2]-r[1], reverse=True)[:60]:
    print(f"L{x[:ln].count(chr(10))+1:>5} | W={w:>3} need={need:>3} fs={fs} | {t} | {ctx[-80:]}")
