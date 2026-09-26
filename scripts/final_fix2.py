# -*- coding: utf-8 -*-
"""修复 final_fix 的写入条件 bug 后重跑逆向修复"""
import io, re, sys, glob, os
sys.stdout.reconfigure(encoding='utf-8')
ROOT = r'D:\doubao space\VioletToolBox\VioletToolBox'
rev_pat1 = re.compile(r'new \(this\.FindControlInPages\("(\w+)"\) as ([A-Za-z0-9_.]+)\)')
rev_pat2 = re.compile(r'\(this\.FindControlInPages\("(\w+)"\) as ([A-Za-z0-9_.]+)\)\.(\w+Property)')
files = glob.glob(os.path.join(ROOT, '*.cs'))
total1 = total2 = 0
for fp in files:
    orig = io.open(fp, 'r', encoding='utf-8').read()
    txt = rev_pat1.sub(lambda m: f'new {m.group(2)}', orig)
    if txt != orig:
        total1 += len(rev_pat1.findall(orig))
    txt2 = rev_pat2.sub(lambda m: f'{m.group(2)}.{m.group(3)}', txt)
    if txt2 != txt:
        total2 += len(rev_pat2.findall(txt))
    if txt2 != orig:
        io.open(fp, 'w', encoding='utf-8', newline='').write(txt2)
        print('written:', os.path.basename(fp))
print(f'reverse fixes: new->{total1}, property->{total2}')
