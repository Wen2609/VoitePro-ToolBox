# -*- coding: utf-8 -*-
import io, re, sys, glob, os
sys.stdout.reconfigure(encoding='utf-8')

# 1) 修 lazy_cs2 提取正则：排除 TargetName
p = r'D:\doubao space\VioletToolBox\lazy_cs2.py'
t = io.open(p, 'r', encoding='utf-8').read()
old = r"r'<(\w+:?[A-Za-z]+)\s+[^>]*?(?:x:Name|Name)=\"([^\"]+)\"'"
new = r"r'<(\w+:?[A-Za-z]+)\s+[^>]*?(?:x:Name|(?<!Target)Name)=\"([^\"]+)\"'"
if old in t:
    t = t.replace(old, new, 1)
    print('extract regex FIXED (exclude TargetName)')
else:
    print('regex anchor NOT FOUND')
io.open(p, 'w', encoding='utf-8', newline='').write(t)

# 2) 用新正则重提取 name2type（exec 前半）
exec(t.split("files = glob.glob")[0])
print('name2type entries:', len(name2type))
if 'border' in name2type:
    print('border ->', name2type['border'])

# 3) 通用修正：所有 (this.FindControlInPages("X") as T) 的 T != name2type[X] → 修正
ROOT = r'D:\doubao space\VioletToolBox\VioletToolBox'
pat = re.compile(r'\(this\.FindControlInPages\("(\w+)"\) as ([A-Za-z0-9_.]+)\)')
total = 0
for fp in glob.glob(os.path.join(ROOT, '*.cs')):
    txt = io.open(fp, 'r', encoding='utf-8').read()
    def fix(m):
        global total
        name, cur = m.group(1), m.group(2)
        want = name2type.get(name)
        if want and want != cur:
            total += 1
            return f'(this.FindControlInPages("{name}") as {want})'
        return m.group(0)
    txt2 = pat.sub(fix, txt)
    if txt2 != txt:
        io.open(fp, 'w', encoding='utf-8', newline='').write(txt2)
        print('fixed:', os.path.basename(fp))
print('as-type fixes:', total)
