# -*- coding: utf-8 -*-
"""1) ns_map 加 local/test1 → WpfApp1 2) Shapes 类型修正 3) 逆向 case 模式变量/局部同名"""
import io, re, sys, glob, os
sys.stdout.reconfigure(encoding='utf-8')

# 1) 修 lazy_cs2 的 ns_map 与 Shapes
p = r'D:\doubao space\VioletToolBox\lazy_cs2.py'
t = io.open(p, 'r', encoding='utf-8').read()
old = "ns_map[''] = 'System.Windows.Controls'"
new = "ns_map[''] = 'System.Windows.Controls'\nfor _p in ('local', 'test1', 'controls', 'custom'):\n    if _p not in ns_map:\n        ns_map[_p] = 'WpfApp1'"
if old in t:
    t = t.replace(old, new, 1)
    print('ns_map local/test1 -> WpfApp1 ADDED')
else:
    print('NS ANCHOR NOT FOUND')
old2 = "    name2type[name] = f'{ns}.{cls}'"
new2 = "    if cls in ('Ellipse', 'Path', 'Rectangle', 'Line', 'Polygon', 'Polyline'):\n        ns = 'System.Windows.Shapes'\n    name2type[name] = f'{ns}.{cls}'"
if old2 in t:
    t = t.replace(old2, new2, 1)
    print('Shapes ns FIXED')
else:
    print('SHAPES ANCHOR NOT FOUND')
io.open(p, 'w', encoding='utf-8', newline='').write(t)

# 2) 逆向：case 模式变量
ROOT = r'D:\doubao space\VioletToolBox\VioletToolBox'
pat_case = re.compile(r'case (\w+) (\w+) when \(this\.FindControlInPages\("\2"\) as [A-Za-z0-9_.]+\)')
total = 0
for fp in glob.glob(os.path.join(ROOT, '*.cs')):
    txt = io.open(fp, 'r', encoding='utf-8').read()
    n = len(pat_case.findall(txt))
    if n:
        txt2 = pat_case.sub(lambda m: f'case {m.group(1)} {m.group(2)} when {m.group(2)}', txt)
        io.open(fp, 'w', encoding='utf-8', newline='').write(txt2)
        total += n
        print('case-pattern reversed:', os.path.basename(fp), n)
print('case fixes:', total)
