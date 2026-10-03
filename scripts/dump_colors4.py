# -*- coding: utf-8 -*-
import re
c = open(r'D:\doubao space\VioletToolBox\VioletToolBox\Themes\Colors.xaml', encoding='utf-8').read()
out = []
# 元素形式: <Color x:Key="Violet500">#HEX</Color>
for m in re.finditer(r'<Color x:Key="(Violet\d+|Gray\d+|Success\d+|Warning\d+|Error\d+|Info\d+)">\s*#([0-9A-Fa-f]+)\s*</Color>', c):
    out.append('%s = #%s' % (m.group(1), m.group(2)))
open(r'D:\doubao space\VioletToolBox\colors4.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('found:', len(out))
