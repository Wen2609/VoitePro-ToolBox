# -*- coding: utf-8 -*-
"""1) lazy_cs2 排除加类型关键字 2) 逆向关键字类型声明误替换 3) 重跑 lazy_cs2"""
import io, re, sys, glob, os
sys.stdout.reconfigure(encoding='utf-8')

# 1) 修 lazy_cs2
p = r'D:\doubao space\VioletToolBox\lazy_cs2.py'
t = io.open(p, 'r', encoding='utf-8').read()
old = "                   or (prev_word and prev_word[0].isupper() and prev_word not in names):"
new = "                   or (prev_word and prev_word[0].isupper() and prev_word not in names) \\\n                   or prev_word in ('double','int','float','long','short','byte','sbyte','uint','ulong','ushort','decimal','char','bool','string','object','void','dynamic','var','nint','nuint'):"
if old in t:
    t = t.replace(old, new, 1)
    print('keyword-type exclusion ADDED')
else:
    print('ANCHOR NOT FOUND')
io.open(p, 'w', encoding='utf-8', newline='').write(t)

# 2) 逆向关键字类型声明误替换
KWT = r'(?:double|int|float|long|short|byte|sbyte|uint|ulong|ushort|decimal|char|bool|string|object|void|dynamic|var|nint|nuint)'
pat = re.compile(r'(' + KWT + r')\s+\(this\.FindControlInPages\("(\w+)"\) as ([A-Za-z0-9_.]+)\)')
ROOT = r'D:\doubao space\VioletToolBox\VioletToolBox'
total = 0
for fp in glob.glob(os.path.join(ROOT, '*.cs')):
    txt = io.open(fp, 'r', encoding='utf-8').read()
    n = len(pat.findall(txt))
    if n:
        txt2 = pat.sub(lambda m: f'{m.group(1)} {m.group(2)}', txt)
        io.open(fp, 'w', encoding='utf-8', newline='').write(txt2)
        total += n
        print('reversed:', os.path.basename(fp), n)
print('keyword-type reverse fixes:', total)
