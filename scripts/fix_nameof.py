# -*- coding: utf-8 -*-
import io, re, sys, glob, os
sys.stdout.reconfigure(encoding='utf-8')
ROOT = r'D:\doubao space\VioletToolBox\VioletToolBox'
pat = re.compile(r'nameof\((MirrorTitleShow\w+CheckBox)\)')
total = 0
for fp in glob.glob(os.path.join(ROOT, '*.cs')):
    txt = io.open(fp, 'r', encoding='utf-8').read()
    n = len(pat.findall(txt))
    if n:
        txt2 = pat.sub(r'"\1"', txt)
        io.open(fp, 'w', encoding='utf-8', newline='').write(txt2)
        total += n
        print(f'{os.path.basename(fp)}: {n}')
print('total nameof fixed:', total)
