# -*- coding: utf-8 -*-
import io, sys
sys.stdout.reconfigure(encoding='utf-8')
p = r'D:\doubao space\VioletToolBox\lazy_cs2.py'
t = io.open(p, 'r', encoding='utf-8').read()
old = """                if prev1 == '.' or prev3.endswith('as ') or before.endswith('is not') \\
                   or prev3.endswith('is ') or before.endswith('nameof(') or before.endswith('typeof(') \\
                   or prev4.endswith('var ') or prev4.endswith('new ') or next_word.isalpha() or next_word == '_':
                    out.append(word)"""
new = """                # 前一个词是类型名（首字母大写且不在控件名集合）→ 声明位置（参数/字段），排除
                pw = i
                while pw > 0 and text[pw-1].isspace(): pw -= 1
                pw_end = pw
                while pw_end > 0 and (text[pw_end-1].isalnum() or text[pw_end-1] == '_'): pw_end -= 1
                prev_word = text[pw_end:pw]
                if prev1 == '.' or prev3.endswith('as ') or before.endswith('is not') \\
                   or prev3.endswith('is ') or before.endswith('nameof(') or before.endswith('typeof(') \\
                   or prev4.endswith('var ') or prev4.endswith('new ') or next_word.isalpha() or next_word == '_' \\
                   or (prev_word and prev_word[0].isupper() and prev_word not in names):
                    out.append(word)"""
if old in t:
    t = t.replace(old, new, 1)
    print('prev-word type-name exclusion ADDED')
else:
    print('ANCHOR NOT FOUND')
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('saved')
