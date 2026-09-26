# -*- coding: utf-8 -*-
"""逆向：声明位置 `类型名 (this.FindControlInPages("X") as T)` → `类型名 X`"""
import io, re, sys, glob, os
sys.stdout.reconfigure(encoding='utf-8')
ROOT = r'D:\doubao space\VioletToolBox\VioletToolBox'
pat = re.compile(r'(?<!new )(\w+(?:<[^>]*>)?)\s+\(this\.FindControlInPages\("(\w+)"\) as ([A-Za-z0-9_.]+)\)')
total = 0
for fp in glob.glob(os.path.join(ROOT, '*.cs')):
    txt = io.open(fp, 'r', encoding='utf-8').read()
    n = len(pat.findall(txt))
    if n:
        txt2 = pat.sub(lambda m: f'{m.group(1)} {m.group(2)}', txt)
        io.open(fp, 'w', encoding='utf-8', newline='').write(txt2)
        total += n
        print(f'{os.path.basename(fp)}: {n}')
print('total declaration fixes:', total)
