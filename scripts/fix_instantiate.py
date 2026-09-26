# -*- coding: utf-8 -*-
import io, sys
sys.stdout.reconfigure(encoding='utf-8')
fp = r'D:\doubao space\VioletToolBox\VioletToolBox\MainWindow.xaml.cs'
t = io.open(fp, 'r', encoding='utf-8').read()
old = """        private FrameworkElement InstantiatePage(string viewName)
        {
            try
            {
                var dt = this.FindResource("Page_" + viewName) as DataTemplate;
                if (dt == null) return null;
                var tmp = new ContentControl { ContentTemplate = dt, Content = new object() };
                tmp.ApplyTemplate();
                var cp = FindVisualChild<ContentPresenter>(tmp);
                if (cp != null && System.Windows.Media.VisualTreeHelper.GetChildrenCount(cp) > 0)
                    return System.Windows.Media.VisualTreeHelper.GetChild(cp, 0) as FrameworkElement;
                return null;
            }
            catch { return null; }
        }"""
new = """        private FrameworkElement InstantiatePage(string viewName)
        {
            try
            {
                var dt = this.FindResource("Page_" + viewName) as DataTemplate;
                if (dt == null) return null;
                return dt.LoadContent() as FrameworkElement;
            }
            catch { return null; }
        }"""
assert old in t, 'InstantiatePage anchor NOT FOUND'
t = t.replace(old, new, 1)
io.open(fp, 'w', encoding='utf-8', newline='').write(t)
print('InstantiatePage now uses DataTemplate.LoadContent()')
