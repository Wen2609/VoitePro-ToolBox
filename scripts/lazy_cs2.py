# -*- coding: utf-8 -*-
"""扫描全部 partial cs：裸控件字段引用 → this.FindControlInPages("X") as T
词法处理：跳过字符串/注释。类型从 XAML tag 推断（含 HandyControl 前缀映射）。"""
import io, re, sys, glob, os
sys.stdout.reconfigure(encoding='utf-8')

ROOT = r'D:\doubao space\VioletToolBox\VioletToolBox'
XAML = os.path.join(ROOT, 'MainWindow.xaml')

c = io.open(XAML, 'r', encoding='utf-8').read()
tpl_region = c  # 全文提取：懒加载模板区 + 主内容区（含恢复的 DownloadView 块）

# ---- 收集 xmlns 前缀映射 ----
ns_map = {}
for m in re.finditer(r'xmlns:(\w+)="([^"]+)"', c):
    url = m.group(2)
    if url.startswith('https://handyorg.github.io/handycontrol'):
        ns_map[m.group(1)] = 'HandyControl.Controls'
    elif 'schemas.microsoft.com/winfx/2006/xaml/presentation' in url:
        ns_map[m.group(1)] = 'System.Windows.Controls'
ns_map[''] = 'System.Windows.Controls'
for _p in ('local', 'test1', 'controls', 'custom'):
    if _p not in ns_map:
        ns_map[_p] = 'test1' if _p == 'test1' else 'WpfApp1'
print('ns map:', ns_map)

# ---- 收集 name → 类型全名 ----
name2type = {}
for m in re.finditer(r'<(\w+:?[A-Za-z]+)\s+[^>]*?(?:x:Name|(?<!Target)Name)="([^"]+)"', tpl_region):
    tag, name = m.group(1), m.group(2)
    if ':' in tag:
        prefix, cls = tag.split(':', 1)
    else:
        prefix, cls = '', tag
    ns = ns_map.get(prefix, 'System.Windows.Controls')
    if cls in ('DataGridTemplateColumn', 'DataGridCheckBoxColumn', 'DataGridComboBoxColumn', 'DataGridTextColumn',
               'DataGridHyperlinkColumn', 'DataGridComboBoxColumn', 'ComboBoxItem', 'Style', 'Setter',
               'DataTemplate', 'ControlTemplate', 'Triggers', 'DataTrigger', 'MultiDataTrigger', 'Condition',
               'Setter', 'EventSetter', 'Storyboard', 'LinearGradientBrush', 'SolidColorBrush', 'GradientStop',
               'DropShadowEffect', 'BooleanToVisibilityConverter', 'ProgressBarIndicatorWidthConverter', 'ScaleTransform',
               'VisualState', 'VisualStateGroup', 'VisualTransition'):
        continue  # 非控件或不需引用
    if cls == 'ToggleButton':
        ns = 'System.Windows.Controls.Primitives'
    if cls == 'ToggleButton':
        ns = 'System.Windows.Controls.Primitives'
    if cls in ('Ellipse', 'Path', 'Rectangle', 'Line', 'Polygon', 'Polyline'):
        ns = 'System.Windows.Shapes'
    name2type[name] = f'{ns}.{cls}'
print('name2type entries:', len(name2type))

# ---- 词法扫描 + 替换 ----
def scan_replace(text, names, name2type):
    # 预替换：this.FindName("模板控件名") → this.FindControlInPages(...)
    text = re.sub(r'this\.FindName\("(' + '|'.join(re.escape(n) for n in sorted(names, key=len, reverse=True)) + r')"\)',
                  lambda m: f'this.FindControlInPages("{m.group(1)}")', text)
    out = []
    i, n = 0, len(text)
    replaced = 0
    while i < n:
        ch = text[i]
        if ch == '/' and i + 1 < n and text[i+1] == '/':
            j = text.find('\n', i)
            if j == -1: j = n
            out.append(text[i:j]); i = j
        elif ch == '/' and i + 1 < n and text[i+1] == '*':
            j = text.find('*/', i + 2)
            if j == -1: j = n
            else: j += 2
            out.append(text[i:j]); i = j
        elif ch == 'u' and text.startswith('using ', i) and '=' in text[i:i+200]:
            # using 别名行整体跳过（目标类型里的控件名不替换）
            j = text.find('\n', i)
            if j == -1: j = n
            out.append(text[i:j]); i = j
        elif ch == "'":
            # C# 字符字面量 'x' / '"'：跳过到配对单引号
            j = i + 1
            while j < n:
                if text[j] == '\\': j += 2; continue
                if text[j] == "'": break
                j += 1
            j = min(j + 1, n)
            out.append(text[i:j]); i = j
        elif ch == '$' and i + 1 < n and text[i+1] == '"':
            # C# 插值字符串 $"..."：表达式内可含字符串/括号
            j = i + 2
            depth = 0
            while j < n:
                c = text[j]
                if c == '\\': j += 2; continue
                if c == '{': depth += 1; j += 1; continue
                if c == '}':
                    if depth == 0: j += 1; break
                    depth -= 1; j += 1; continue
                if c == '"':
                    if depth == 0: j += 1; break
                    j2 = j + 1
                    while j2 < n:
                        if text[j2] == '\\': j2 += 2; continue
                        if text[j2] == '"': break
                        j2 += 1
                    j = min(j2 + 1, n); continue
                j += 1
            j = min(j, n)
            out.append(text[i:j]); i = j
        elif ch == '"':
            j = i + 1
            while j < n:
                if text[j] == '\\': j += 2; continue
                if text[j] == '"': break
                j += 1
            j = min(j + 1, n)
            out.append(text[i:j]); i = j
        elif ch == '@' and i + 1 < n and text[i+1] == '"':
            # verbatim string
            j = i + 2
            while j < n:
                if text[j] == '"' and j + 1 < n and text[j+1] == '"': j += 2; continue
                if text[j] == '"': break
                j += 1
            j = min(j + 1, n)
            out.append(text[i:j]); i = j
        elif ch.isalpha() or ch == '_':
            j = i + 1
            while j < n and (text[j].isalnum() or text[j] == '_'): j += 1
            word = text[i:j]
            if word in names:
                t = name2type.get(word, 'System.Windows.FrameworkElement')
                # 排除声明/类型上下文：using 别名、as/is/is not、nameof(、typeof(、命名空间限定(.)
                prev1 = text[i-1] if i > 0 else ''
                before = text[max(0, i-7):i].rstrip()
                prev3 = text[max(0, i-3):i]
                prev4 = text[max(0, i-4):i]
                k = j
                while k < n and text[k].isspace(): k += 1
                next_word = text[k] if k < n else ''
                # 前一个词是类型名（首字母大写且不在控件名集合）→ 声明位置（参数/字段），排除
                pw = i
                while pw > 0 and text[pw-1].isspace(): pw -= 1
                pw_end = pw
                while pw_end > 0 and (text[pw_end-1].isalnum() or text[pw_end-1] == '_'): pw_end -= 1
                prev_word = text[pw_end:pw]
                if prev1 == '.' or prev3.endswith('as ') or before.endswith('is not') \
                   or prev3.endswith('is ') or before.endswith('nameof(') or before.endswith('typeof(') \
                   or prev4.endswith('var ') or prev4.endswith('new ') or next_word.isalpha() or next_word == '_' \
                   or (prev_word and prev_word[0].isupper() and prev_word not in names) \
                   or prev_word in ('double','int','float','long','short','byte','sbyte','uint','ulong','ushort','decimal','char','bool','string','object','void','dynamic','var','nint','nuint'):
                    out.append(word)
                else:
                    out.append(f'(this.FindControlInPages("{word}") as {t})')
                    replaced += 1
            else:
                out.append(word)
            i = j
        else:
            out.append(ch); i += 1
    return ''.join(out), replaced

# 裸引用排除：已被 FindControlInPages("X") 包裹的 X（脚本上一轮已替换 this.FindName）
# 若 X 出现在 this.FindControlInPages("X") 内，其左右是 " 和 )，词法扫描会把它当字符串内容跳过 ✓ 天然安全
# 但裸 X 与 FindControlInPages("X") 并存：FindControlInPages 调用里 X 在字符串中 ✓ 不会重复替换

files = glob.glob(os.path.join(ROOT, 'MainWindow*.cs')) + [os.path.join(ROOT, 'oujiaflash.cs'), os.path.join(ROOT, 'RomDownload.cs')]
total = 0
for fp in sorted(files):
    base = os.path.basename(fp)
    if base == 'MainWindow.xaml.cs':
        continue  # 上一脚本已处理 this.FindName；裸引用也在此文件，同样处理（跳过重复注入 helper 风险）
    txt = io.open(fp, 'r', encoding='utf-8').read()
    new_txt, rep = scan_replace(txt, set(name2type.keys()), name2type)
    if rep:
        io.open(fp, 'w', encoding='utf-8', newline='').write(new_txt)
        print(f'{base}: replaced {rep}')
        total += rep
    else:
        print(f'{base}: 0')

# 也处理 MainWindow.xaml.cs 的裸引用（排除 helper 区域行号外所有裸引用）
fp = os.path.join(ROOT, 'MainWindow.xaml.cs')
txt = io.open(fp, 'r', encoding='utf-8').read()
new_txt, rep = scan_replace(txt, set(name2type.keys()), name2type)
if rep:
    io.open(fp, 'w', encoding='utf-8', newline='').write(new_txt)
    print(f'MainWindow.xaml.cs: replaced {rep}')
    total += rep
print('TOTAL replaced:', total)
