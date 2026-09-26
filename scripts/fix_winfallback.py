# -*- coding: utf-8 -*-
import io, sys
sys.stdout.reconfigure(encoding='utf-8')
csfp = r'D:\doubao space\VioletToolBox\VioletToolBox\MainWindow.xaml.cs'
t = io.open(csfp, 'r', encoding='utf-8').read()
old = """            if (_pageHost != null)
            {
                var f = FindByName(_pageHost, name);
                if (f != null) { _nameViewMap[name] = "HomeView"; return f; }
            }"""
new = """            if (_pageHost != null)
            {
                var f = FindByName(_pageHost, name);
                if (f != null) { _nameViewMap[name] = "HomeView"; return f; }
            }
            var wf = FindByName(this, name);
            if (wf != null) { _nameViewMap[name] = "HomeView"; return wf; }"""
assert old in t, 'FindControlInPages anchor NOT FOUND'
t = t.replace(old, new, 1)
io.open(csfp, 'w', encoding='utf-8', newline='').write(t)
print('window-level fallback added to FindControlInPages')
