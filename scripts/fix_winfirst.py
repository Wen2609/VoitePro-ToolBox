# -*- coding: utf-8 -*-
import io, sys
sys.stdout.reconfigure(encoding='utf-8')
csfp = r'D:\doubao space\VioletToolBox\VioletToolBox\MainWindow.xaml.cs'
t = io.open(csfp, 'r', encoding='utf-8').read()
old = """        private object FindControlInPages(string name)
        {
            string sVn = StaticNameView(name);"""
new = """        private object FindControlInPages(string name)
        {
            var wf0 = FindByName(this, name);
            if (wf0 != null) return wf0;
            string sVn = StaticNameView(name);"""
assert old in t, 'anchor NOT FOUND'
t = t.replace(old, new, 1)
io.open(csfp, 'w', encoding='utf-8', newline='').write(t)
print('window-level fast lookup added at start of FindControlInPages')
