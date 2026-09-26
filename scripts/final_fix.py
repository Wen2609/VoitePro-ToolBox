# -*- coding: utf-8 -*-
"""最终修复：
1) 逆向固化错误：new (FindControlInPages...) → new T；(FindControlInPages...).XxxProperty → T.XxxProperty
2) 插值字符串表达式内的控件引用：{X...} → {(FindControlInPages("X") as T)...
3) 重跑 lazy_cs2 补漏
"""
import io, re, sys, glob, os
sys.stdout.reconfigure(encoding='utf-8')

ROOT = r'D:\doubao space\VioletToolBox\VioletToolBox'

# 1) 逆向修复
rev_pat1 = re.compile(r'new \(this\.FindControlInPages\("(\w+)"\) as ([A-Za-z0-9_.]+)\)')
rev_pat2 = re.compile(r'\(this\.FindControlInPages\("(\w+)"\) as ([A-Za-z0-9_.]+)\)\.(\w+Property)')

files = glob.glob(os.path.join(ROOT, '*.cs'))
total1 = total2 = 0
for fp in files:
    txt = io.open(fp, 'r', encoding='utf-8').read()
    t1 = rev_pat1.sub(lambda m: f'new {m.group(2)}', txt)
    if t1 != txt:
        total1 += len(rev_pat1.findall(txt))
        txt = t1
    t2 = rev_pat2.sub(lambda m: f'{m.group(2)}.{m.group(3)}', txt)
    if t2 != txt:
        total2 += len(rev_pat2.findall(txt))
        txt = t2
    if t1 != txt or t2 != txt:
        io.open(fp, 'w', encoding='utf-8', newline='').write(txt)
print(f'reverse fixes: new->{total1}, property->{total2}')

# 2) 插值表达式控件替换（需要 names 集合，复用 lazy_cs2 的提取）
exec(io.open(r'D:\doubao space\VioletToolBox\lazy_cs2.py', 'r', encoding='utf-8').read().split("files = glob.glob")[0])
# 上述 exec 定义 name2type；写独立替换
def repl_interp(m, names=set(name2type.keys()), nt=name2type):
    name = m.group(1)
    if name in names:
        t = nt.get(name, 'System.Windows.FrameworkElement')
        return f'{{(this.FindControlInPages("{name}") as {t})'
    return m.group(0)

interp_pat = re.compile(r'\{(\w+)(?=[\?\.\]\}\s,])')
total3 = 0
for fp in files:
    txt = io.open(fp, 'r', encoding='utf-8').read()
    new_txt = interp_pat.sub(repl_interp, txt)
    if new_txt != txt:
        total3 += 1
        io.open(fp, 'w', encoding='utf-8', newline='').write(new_txt)
        print('interp fixed:', os.path.basename(fp))
print('interp fixes:', total3)
