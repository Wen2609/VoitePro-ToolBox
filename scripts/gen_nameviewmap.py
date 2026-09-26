# -*- coding: utf-8 -*-
"""从 XAML 16 个模板提取 x:Name→View 映射，生成 C# 字典代码"""
import io, re, sys
sys.stdout.reconfigure(encoding='utf-8')
fp = r'D:\doubao space\VioletToolBox\VioletToolBox\MainWindow.xaml'
x = io.open(fp, 'r', encoding='utf-8').read()

# 找 16 个模板（x:Key="Page_X" 或 DISABLED_）
tpl_re = re.compile(r'<DataTemplate\s+x:Key="(?:DISABLED_)?(Page_[A-Za-z0-9]+)">')
tpls = []
for m in tpl_re.finditer(x):
    tpls.append((m.start(), m.end(), m.group(1)))

name_view = {}
for i, (s, e, key) in enumerate(tpls):
    end = tpls[i + 1][0] if i + 1 < len(tpls) else x.find('</FrameworkElement.Resources>', s)
    seg = x[s:end]
    # 模板内所有 x:Name 和 Name= 属性（排除 TargetName、Storyboard.TargetName）
    for m in re.finditer(r'\b(?:x:Name|Name)="([^"]+)"', seg):
        nm = m.group(1)
        if nm.startswith('DISABLED_'):
            continue
        if nm not in name_view:
            name_view[nm] = key

print('mapped names:', len(name_view))
# 生成 C# 字典（分块）
items = sorted(name_view.items())
chunks = [items[i:i + 60] for i in range(0, len(items), 60)]
lines = []
for ci, chunk in enumerate(chunks):
    lines.append('        private static readonly System.Collections.Generic.Dictionary<string, string> _nameViewMapStatic%d = new System.Collections.Generic.Dictionary<string, string>();' % ci)
    lines.append('        static MainWindow()')
    lines.append('        {')
    for nm, key in chunk:
        lines.append('            _nameViewMapStatic%d["%s"] = "%s";' % (ci, nm.replace('"', '\\"'), key))
    lines.append('        }')
    lines.append('')
code = '\n'.join(lines)
io.open(r'D:\doubao space\VioletToolBox\name_view_map.cs.txt', 'w', encoding='utf-8', newline='').write(code)
print('C# map code written to name_view_map.cs.txt, lines:', len(lines))
# 统计每页控件数
from collections import Counter
cnt = Counter(v for v in name_view.values())
for k, v in sorted(cnt.items()):
    print(' ', k, v)
