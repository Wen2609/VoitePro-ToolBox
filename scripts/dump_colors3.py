# -*- coding: utf-8 -*-
import re
c = open(r'D:\doubao space\VioletToolBox\VioletToolBox\Themes\Colors.xaml', encoding='utf-8').read()
out = []
for m in re.finditer(r'x:Key="(Violet\d+)"[^>]*?(?:Color="([^"]+)")?', c):
    out.append('%s = %s' % (m.group(1), m.group(2) or '?'))
for m in re.finditer(r'x:Key="(Gray\d+)"[^>]*?(?:Color="([^"]+)")?', c):
    out.append('%s = %s' % (m.group(1), m.group(2) or '?'))
open(r'D:\doubao space\VioletToolBox\colors3.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('done')
