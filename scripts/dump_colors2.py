# -*- coding: utf-8 -*-
import re
c = open(r'D:\doubao space\VioletToolBox\VioletToolBox\Themes\Colors.xaml', encoding='utf-8').read()
out = []
# 所有 Color 定义
for m in re.finditer(r'x:Key="([^"]+)"\s+Color="([^"]+)"', c):
    out.append('%s = %s' % (m.group(1), m.group(2)))
open(r'D:\doubao space\VioletToolBox\colors2.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('total color keys:', len(out))
