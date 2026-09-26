# -*- coding: utf-8 -*-
import io, sys
sys.stdout.reconfigure(encoding='utf-8')
csfp = r'D:\doubao space\VioletToolBox\VioletToolBox\MainWindow.xaml.cs'
t = io.open(csfp, 'r', encoding='utf-8').read()
old = """        private FrameworkElement InstantiatePage(string viewName)
        {
            try
            {
                var dt = this.FindResource("Page_" + viewName) as DataTemplate;
                if (dt == null) return null;
                return dt.LoadContent() as FrameworkElement;
            }
            catch { return null; }
        }"""
new = """        private FrameworkElement InstantiatePage(string viewName)
        {
            try
            {
                var dt = this.FindResource("Page_" + viewName) as DataTemplate;
                if (dt == null) return null;
                try { System.IO.File.AppendAllText(System.IO.Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "startup.log"), "LC " + viewName + " before\\r\\n"); } catch { }
                var r = dt.LoadContent() as FrameworkElement;
                try { System.IO.File.AppendAllText(System.IO.Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "startup.log"), "LC " + viewName + " after\\r\\n"); } catch { }
                return r;
            }
            catch { return null; }
        }"""
assert old in t, 'InstantiatePage anchor NOT FOUND'
t = t.replace(old, new, 1)
io.open(csfp, 'w', encoding='utf-8', newline='').write(t)
print('InstantiatePage diag added')
