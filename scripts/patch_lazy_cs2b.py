# -*- coding: utf-8 -*-
import io, sys
sys.stdout.reconfigure(encoding='utf-8')
p = r'D:\doubao space\VioletToolBox\lazy_cs2.py'
t = io.open(p, 'r', encoding='utf-8').read()

old = '''        elif ch == '$' and i + 1 < n and text[i+1] == '"':'''
new = '''        elif ch == "'":
            # C# 字符字面量 'x' / '"'：跳过到配对单引号
            j = i + 1
            while j < n:
                if text[j] == '\\\\': j += 2; continue
                if text[j] == "'": break
                j += 1
            j = min(j + 1, n)
            out.append(text[i:j]); i = j
        elif ch == '$' and i + 1 < n and text[i+1] == '"':'''
if old in t:
    t = t.replace(old, new, 1)
    print('char-literal branch ADDED')
else:
    print('ANCHOR NOT FOUND')
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('saved')
