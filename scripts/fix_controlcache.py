# -*- coding: utf-8 -*-
import io, sys
sys.stdout.reconfigure(encoding='utf-8')
csfp = r'D:\doubao space\VioletToolBox\VioletToolBox\MainWindow.xaml.cs'
t = io.open(csfp, 'r', encoding='utf-8').read()

# 1) 加 _controlCache 字段（_instantiating 后）
old_f = """        private readonly System.Collections.Generic.HashSet<string> _instantiating = new System.Collections.Generic.HashSet<string>();"""
new_f = """        private readonly System.Collections.Generic.HashSet<string> _instantiating = new System.Collections.Generic.HashSet<string>();
        private readonly System.Collections.Generic.Dictionary<string, FrameworkElement> _controlCache = new System.Collections.Generic.Dictionary<string, FrameworkElement>();"""
assert old_f in t, 'field anchor NOT FOUND'
t = t.replace(old_f, new_f, 1)
print('_controlCache field added')

# 2) FindControlInPages 包缓存：方法头加缓存检查，所有 return 写缓存
old_m = """        private object FindControlInPages(string name)
        {
            var wf0 = FindByName(this, name);
            if (wf0 != null) return wf0;
            string sVn = StaticNameView(name);"""
new_m = """        private object FindControlInPages(string name)
        {
            if (_controlCache.TryGetValue(name, out var _cc)) return _cc;
            var _res = FindControlInPagesCore(name);
            if (_res is FrameworkElement _cfe) _controlCache[name] = _cfe;
            return _res;
        }

        private object FindControlInPagesCore(string name)
        {
            var wf0 = FindByName(this, name);
            if (wf0 != null) return wf0;
            string sVn = StaticNameView(name);"""
assert old_m in t, 'method head anchor NOT FOUND'
t = t.replace(old_m, new_m, 1)
print('cache wrapper added')

io.open(csfp, 'w', encoding='utf-8', newline='').write(t)
print('done')
