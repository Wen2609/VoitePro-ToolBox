# -*- coding: utf-8 -*-
import io, sys
sys.stdout.reconfigure(encoding='utf-8')
p = r'D:\doubao space\VioletToolBox\lazy_cs2.py'
t = io.open(p, 'r', encoding='utf-8').read()
old = "re.finditer(r'<(\\w+:?[A-Za-z]+)\\s+[^>]*?(?:x:Name|Name)=\"([^\"]+)\"', tpl_region)"
new = "re.finditer(r'<(\\w+:?[A-Za-z]+)\\s+[^>]*?(?:x:Name|(?<!Target)Name)=\"([^\"]+)\"', tpl_region)"
if old in t:
    t = t.replace(old, new, 1)
    print('regex FIXED')
else:
    # 打印实际行
    for line in t.split('\n'):
        if 'x:Name|Name' in line:
            print('ACTUAL:', repr(line))
            # 构造匹配版本
            idx = t.find(line)
            fixed = line.replace('(?:x:Name|Name)=', '(?:x:Name|(?<!Target)Name)=')
            t = t[:idx] + fixed + t[idx+len(line):]
            print('FIXED via line replace')
            break
    else:
        print('STILL NOT FOUND')
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('saved')
