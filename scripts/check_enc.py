# -*- coding: utf-8 -*-
import io, sys
sys.stdout.reconfigure(encoding='utf-8')
fp = r'D:\doubao space\VioletToolBox\VioletToolBox\MainWindow.EdlFlash.cs'
raw = open(fp, 'rb').read(400)
print('BOM:', raw[:3])
print('first bytes:', raw[:40])
# 尝试解码
for enc in ('utf-8', 'gbk'):
    try:
        open(fp, 'rb').read().decode(enc)
        print(enc, 'decode OK')
    except Exception as e:
        print(enc, 'FAIL', e)
