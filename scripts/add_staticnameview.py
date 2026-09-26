# -*- coding: utf-8 -*-
import io, sys
sys.stdout.reconfigure(encoding='utf-8')
csfp = r'D:\doubao space\VioletToolBox\VioletToolBox\MainWindow.xaml.cs'
t = io.open(csfp, 'r', encoding='utf-8').read()
if 'private static string StaticNameView' in t:
    print('StaticNameView already present')
else:
    anchor = """        private void CollectPageTemplateKeys()
        {
            foreach (var key in this.Resources.Keys)
            {
                if (key is string s && s.StartsWith("Page_") && !_pageTemplateKeys.Contains(s))
                    _pageTemplateKeys.Add(s);
            }
        }"""
    helper = anchor + """

        private static string StaticNameView(string name)
        {
            foreach (var d in _nameViewMapStaticAll)
            {
                if (d.TryGetValue(name, out var v)) return v;
            }
            return null;
        }"""
    assert anchor in t, 'helper anchor NOT FOUND'
    t = t.replace(anchor, helper, 1)
    io.open(csfp, 'w', encoding='utf-8', newline='').write(t)
    print('StaticNameView helper added')
