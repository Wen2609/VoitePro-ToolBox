# -*- coding: utf-8 -*-
import io, re, sys
sys.stdout.reconfigure(encoding='utf-8')
fp = r'D:\doubao space\VioletToolBox\VioletToolBox\MainWindow.xaml'
x = io.open(fp, 'r', encoding='utf-8').read()
before = x
x = re.sub(r'[ \t]*AllowsTransparency="True"\r?\n', '', x, count=1)
x = re.sub(r'[ \t]*Background="#00FFFFFF"', 'Background="#FFFAFAFC"', x, count=1)
assert x != before, 'no change - anchors not found'
io.open(fp, 'w', encoding='utf-8', newline='').write(x)
print('transparency removed; solid bg set')
