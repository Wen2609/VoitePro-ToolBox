# -*- coding: utf-8 -*-
import io, sys
sys.stdout.reconfigure(encoding='utf-8')
p = r'D:\doubao space\VioletToolBox\lazy_cs2.py'
t = io.open(p, 'r', encoding='utf-8').read()

# 1) 加 $" 插值字符串分支
old1 = '''        elif ch == '"':
            j = i + 1
            while j < n:
                if text[j] == '\\\\': j += 2; continue
                if text[j] == '"': break
                j += 1
            j = min(j + 1, n)
            out.append(text[i:j]); i = j'''
new1 = '''        elif ch == '$' and i + 1 < n and text[i+1] == '"':
            # C# 插值字符串 $"..."：表达式内可含字符串/括号
            j = i + 2
            depth = 0
            while j < n:
                c = text[j]
                if c == '\\\\': j += 2; continue
                if c == '{': depth += 1; j += 1; continue
                if c == '}':
                    if depth == 0: j += 1; break
                    depth -= 1; j += 1; continue
                if c == '"':
                    if depth == 0: j += 1; break
                    j2 = j + 1
                    while j2 < n:
                        if text[j2] == '\\\\': j2 += 2; continue
                        if text[j2] == '"': break
                        j2 += 1
                    j = min(j2 + 1, n); continue
                j += 1
            j = min(j, n)
            out.append(text[i:j]); i = j
        elif ch == '"':
            j = i + 1
            while j < n:
                if text[j] == '\\\\': j += 2; continue
                if text[j] == '"': break
                j += 1
            j = min(j + 1, n)
            out.append(text[i:j]); i = j'''
if old1 in t:
    t = t.replace(old1, new1, 1)
    print('A: interpolated-string branch ADDED')
else:
    print('A NOT FOUND')

# 2) new 排除
old2 = "                   or prev4.endswith('var ') or next_word.isalpha() or next_word == '_':"
new2 = "                   or prev4.endswith('var ') or prev4.endswith('new ') or next_word.isalpha() or next_word == '_':"
if old2 in t:
    t = t.replace(old2, new2, 1)
    print('B: new-exclusion ADDED')
else:
    print('B NOT FOUND')

io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('saved')
