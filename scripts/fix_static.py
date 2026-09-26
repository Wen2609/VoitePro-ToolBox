# -*- coding: utf-8 -*-
"""1) lazy_cs2 映射修正（test1/ToggleButton/MenuItem） 2) 逆向静态方法体与 FrameworkElementFactory 方法体内的替换"""
import io, re, sys, glob, os
sys.stdout.reconfigure(encoding='utf-8')

# ---- 1) 修 lazy_cs2 ----
p = r'D:\doubao space\VioletToolBox\lazy_cs2.py'
t = io.open(p, 'r', encoding='utf-8').read()
# test1 命名空间
t = t.replace("ns_map[_p] = 'WpfApp1'", "ns_map[_p] = 'test1' if _p == 'test1' else 'WpfApp1'")
# ToggleButton
old3 = "    if cls in ('Ellipse', 'Path', 'Rectangle', 'Line', 'Polygon', 'Polyline'):"
new3 = "    if cls == 'ToggleButton':\n        ns = 'System.Windows.Controls.Primitives'\n    if cls in ('Ellipse', 'Path', 'Rectangle', 'Line', 'Polygon', 'Polyline'):"
t = t.replace(old3, new3, 1)
# MenuItem 从排除移除
t = t.replace("'DataGridHyperlinkColumn', 'DataGridComboBoxColumn', 'ComboBoxItem', 'MenuItem', 'Style', 'Setter',",
              "'DataGridHyperlinkColumn', 'DataGridComboBoxColumn', 'ComboBoxItem', 'Style', 'Setter',")
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('lazy_cs2 mapping FIXED (test1/ToggleButton/MenuItem)')

# ---- 2) 逆向工具 ----
REPL = re.compile(r'\(this\.FindControlInPages\("(\w+)"\) as [A-Za-z0-9_.]+\)')

def find_method(text, err_line):
    """按行号 err_line(1-based) 找所在方法体 [start,end)（字符区间），返回方法签名行号"""
    lines = text.split('\n')
    # 向上找方法签名：含 '(' ')' 且以 ')' 或 '{' 结束的行，且前面有 private/static/public/internal
    sig = None
    for k in range(err_line - 1, -1, -1):
        ln = lines[k]
        s = ln.strip()
        if ('static' in s or 'private' in s or 'public' in s or 'internal' in s) and '{' in ln:
            sig = k
            break
        if sig is None and ('static' in s or s.startswith(('private', 'public', 'internal'))) and ')' in ln:
            sig = k
            break
    if sig is None:
        return None
    # 从 sig 行找 '{'
    brace_start = None
    depth = 0
    for k in range(sig, len(lines)):
        for ch in lines[k]:
            if ch == '{':
                if depth == 0 and brace_start is None:
                    brace_start = k
                depth += 1
            elif ch == '}':
                depth -= 1
                if depth == 0 and brace_start is not None:
                    return sig, brace_start, k + 1  # 行区间（含闭行）
    return None

ROOT = r'D:\doubao space\VioletToolBox\VioletToolBox'
jobs = [
    (r'MainWindow.EdlFlash.cs', [8247]),
    (r'MainWindow.EdlFeedback.cs', [405, 406]),
    (r'MainWindow.Payload.cs', [710, 1104, 1105]),
]
total = 0
for fn, err_lines in jobs:
    fp = os.path.join(ROOT, fn)
    txt = io.open(fp, 'r', encoding='utf-8').read()
    done_ranges = []
    for el in err_lines:
        r = find_method(txt, el)
        if not r:
            print(fn, 'method not found for line', el)
            continue
        sig, bs, be = r
        if any(sig == d[0] for d in done_ranges):
            continue
        done_ranges.append((sig, bs, be))
    # 按行区间逆向
    lines = txt.split('\n')
    changed = False
    for sig, bs, be in done_ranges:
        # 拼接区间文本
        seg = '\n'.join(lines[bs:be])
        n = len(REPL.findall(seg))
        if n:
            seg2 = REPL.sub(lambda m: m.group(1), seg)
            lines[bs:be] = seg2.split('\n')
            changed = True
            total += n
            print(fn, f'method at L{sig+1}: reversed {n}')
    if changed:
        io.open(fp, 'w', encoding='utf-8', newline='').write('\n'.join(lines))
print('static-method reversals:', total)

# ---- 3) 逆向 BuildScrcpyControlBarButtonTemplate 方法体（xaml.cs） ----
fp = os.path.join(ROOT, 'MainWindow.xaml.cs')
txt = io.open(fp, 'r', encoding='utf-8').read()
start = txt.find('private FrameworkElementFactory BuildScrcpyControlBarButtonTemplate()')
if start >= 0:
    # 括号匹配方法体
    brace = txt.find('{', start)
    depth = 0
    end = brace
    i = brace
    while i < len(txt):
        if txt[i] == '{': depth += 1
        elif txt[i] == '}':
            depth -= 1
            if depth == 0:
                end = i + 1
                break
        i += 1
    body = txt[brace:end]
    n = len(REPL.findall(body))
    if n:
        body2 = REPL.sub(lambda m: m.group(1), body)
        txt = txt[:brace] + body2 + txt[end:]
        io.open(fp, 'w', encoding='utf-8', newline='').write(txt)
        print('BuildScrcpyControlBarButtonTemplate reversed:', n)
else:
    print('BuildScrcpy... NOT FOUND')
