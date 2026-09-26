# -*- coding: utf-8 -*-
import io, sys
sys.stdout.reconfigure(encoding='utf-8')
for f in ['pf_out.txt', 'r1_out.txt', 'r2_out.txt']:
    print('===', f)
    t = io.open(r'D:\doubao space\VioletToolBox\\' + f, 'r', encoding='utf-8').read()
    lines = t.strip().split('\n')
    print('\n'.join(lines[-14:]))
