# -*- coding: utf-8 -*-
import io, re, sys
sys.stdout.reconfigure(encoding='utf-8')
# 1) 重生成映射（值去 Page_ 前缀）
fp = r'D:\doubao space\VioletToolBox\VioletToolBox\MainWindow.xaml'
x = io.open(fp, 'r', encoding='utf-8').read()
tpl_re = re.compile(r'<DataTemplate\s+x:Key="(?:DISABLED_)?(Page_[A-Za-z0-9]+)">')
tpls = []
for m in tpl_re.finditer(x):
    tpls.append((m.start(), m.end(), m.group(1)))
name_view = {}
for i, (s, e, key) in enumerate(tpls):
    end = tpls[i + 1][0] if i + 1 < len(tpls) else x.find('</FrameworkElement.Resources>', s)
    seg = x[s:end]
    for m in re.finditer(r'\b(?:x:Name|Name)="([^"]+)"', seg):
        nm = m.group(1)
        if nm.startswith('DISABLED_'):
            continue
        if nm not in name_view:
            name_view[nm] = key[len('Page_'):]  # 去前缀

items = sorted(name_view.items())
chunks = [items[i:i + 80] for i in range(0, len(items), 80)]
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
print('map regenerated, names:', len(name_view), 'chunks:', len(chunks))

# 2) 注入 MainWindow.xaml.cs：静态字典 + 静态映射查找辅助
csfp = r'D:\doubao space\VioletToolBox\VioletToolBox\MainWindow.xaml.cs'
t = io.open(csfp, 'r', encoding='utf-8').read()
# 注入静态字典（在类内合适位置：_pageInstances 字段前）
anchor = """        // ===== 懒加载页面支持（2026-09 性能重构） =====
        private readonly Dictionary<string, FrameworkElement> _pageInstances = new Dictionary<string, FrameworkElement>();"""
if '_nameViewMapStatic0' not in t:
    assert anchor in t, 'inject anchor NOT FOUND'
    t = t.replace(anchor, code + "\n" + anchor, 1)
    print('static map injected')
else:
    print('static map already present')

# 3) FindControlInPages：先查静态映射
old = """        private object FindControlInPages(string name)
        {
            if (_nameViewMap.TryGetValue(name, out var vn))"""
new = """        private object FindControlInPages(string name)
        {
            string sVn = StaticNameView(name);
            if (sVn != null)
            {
                if (_pageInstances.TryGetValue(sVn, out var sInst))
                    return FindByName(sInst, name);
                var sNew = InstantiatePage(sVn);
                if (sNew == null) return null;
                _pageInstances[sVn] = sNew;
                return FindByName(sNew, name);
            }
            if (_nameViewMap.TryGetValue(name, out var vn))"""
assert old in t, 'FindControlInPages anchor NOT FOUND'
t = t.replace(old, new, 1)

# 4) 加 StaticNameView 辅助（放在 CollectPageTemplateKeys 后）
anchor2 = """        private void CollectPageTemplateKeys()
        {
            foreach (var key in this.Resources.Keys)
            {
                if (key is string s && s.StartsWith("Page_") && !_pageTemplateKeys.Contains(s))
                    _pageTemplateKeys.Add(s);
            }
        }"""
helper = anchor2 + """

        private static string StaticNameView(string name)
        {
            foreach (var d in _nameViewMapStaticAll)
            {
                if (d.TryGetValue(name, out var v)) return v;
            }
            return null;
        }"""
if 'StaticNameView(' not in t:
    assert anchor2 in t, 'helper anchor NOT FOUND'
    t = t.replace(anchor2, helper, 1)
    print('StaticNameView helper added')
# _nameViewMapStaticAll 数组字段（放在静态字典块后）
arr_anchor = "        // ===== 懒加载页面支持（2026-09 性能重构） =====\n"
arr = "        private static readonly System.Collections.Generic.Dictionary<string, string>[] _nameViewMapStaticAll = new System.Collections.Generic.Dictionary<string, string>[] { _nameViewMapStatic0 };"
# 数 chunk 数动态生成数组
chunk_names = ', '.join('_nameViewMapStatic%d' % i for i in range(len(chunks)))
arr = "        private static readonly System.Collections.Generic.Dictionary<string, string>[] _nameViewMapStaticAll = new System.Collections.Generic.Dictionary<string, string>[] { %s };" % chunk_names
if '_nameViewMapStaticAll' not in t:
    # 插在最后一个静态字典块后（即 code 的尾部）——用 anchor：懒加载注释前插数组
    t = t.replace(arr_anchor, arr + "\n" + arr_anchor, 1)
    print('static array injected')
io.open(csfp, 'w', encoding='utf-8', newline='').write(t)
print('injection complete')
