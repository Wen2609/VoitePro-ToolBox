# -*- coding: utf-8 -*-
import io, re, sys, glob, os
sys.stdout.reconfigure(encoding='utf-8')
# 1) lazy_cs2 排除加 VisualState 系列
p = r'D:\doubao space\VioletToolBox\lazy_cs2.py'
t = io.open(p, 'r', encoding='utf-8').read()
old = "'DropShadowEffect', 'BooleanToVisibilityConverter', 'ProgressBarIndicatorWidthConverter', 'ScaleTransform'):"
new = "'DropShadowEffect', 'BooleanToVisibilityConverter', 'ProgressBarIndicatorWidthConverter', 'ScaleTransform',\n               'VisualState', 'VisualStateGroup', 'VisualTransition'):"
if old in t:
    t = t.replace(old, new, 1)
    print('VisualState exclusion ADDED')
else:
    print('ANCHOR NOT FOUND')
io.open(p, 'w', encoding='utf-8', newline='').write(t)

# 2) 逆向 Normal 误替换（全 cs）
pat = re.compile(r'\(this\.FindControlInPages\("Normal"\) as System\.Windows\.Controls\.VisualState\)')
total = 0
for fp in glob.glob(os.path.join(r'D:\doubao space\VioletToolBox\VioletToolBox', '*.cs')):
    txt = io.open(fp, 'r', encoding='utf-8').read()
    n = len(pat.findall(txt))
    if n:
        txt2 = pat.sub('Normal', txt)
        io.open(fp, 'w', encoding='utf-8', newline='').write(txt2)
        total += n
        print(os.path.basename(fp), n)
print('Normal reversals:', total)
