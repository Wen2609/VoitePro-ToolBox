# -*- coding: utf-8 -*-
import io, sys
sys.stdout.reconfigure(encoding='utf-8')
p = r'D:\doubao space\VioletToolBox\lazy_cs2.py'
t = io.open(p, 'r', encoding='utf-8').read()
old = "files = glob.glob(os.path.join(ROOT, 'MainWindow*.cs'))"
new = "files = glob.glob(os.path.join(ROOT, 'MainWindow*.cs')) + [os.path.join(ROOT, 'oujiaflash.cs'), os.path.join(ROOT, 'RomDownload.cs')]"
if old in t:
    t = t.replace(old, new, 1)
    print('glob EXTENDED (oujiaflash/RomDownload)')
else:
    print('ANCHOR NOT FOUND')
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('saved')
