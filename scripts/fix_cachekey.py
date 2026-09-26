# -*- coding: utf-8 -*-
import io, sys
sys.stdout.reconfigure(encoding='utf-8')
fp = r'D:\doubao space\VioletToolBox\VioletToolBox\MainWindow.xaml.cs'
t = io.open(fp, 'r', encoding='utf-8').read()

old = """            foreach (var key in _pageTemplateKeys)
            {
                if (_pageInstances.ContainsKey(key)) continue;
                var inst = InstantiatePage(key);
                if (inst == null) continue;
                _pageInstances[key] = inst;
                var f2 = FindByName(inst, name);
                if (f2 != null) return f2;
            }"""
new = """            foreach (var key in _pageTemplateKeys)
            {
                var vn = key.StartsWith("Page_") ? key.Substring("Page_".Length) : key;
                if (_pageInstances.ContainsKey(vn)) continue;
                var inst = InstantiatePage(vn);
                if (inst == null) continue;
                _pageInstances[vn] = inst;
                var f2 = FindByName(inst, name);
                if (f2 != null) return f2;
            }"""
assert old in t, 'lazy anchor NOT FOUND'
t = t.replace(old, new, 1)
io.open(fp, 'w', encoding='utf-8', newline='').write(t)
print('cache key normalized')
