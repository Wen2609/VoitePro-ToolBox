# -*- coding: utf-8 -*-
import io, sys
sys.stdout.reconfigure(encoding='utf-8')
csfp = r'D:\doubao space\VioletToolBox\VioletToolBox\MainWindow.xaml.cs'
t = io.open(csfp, 'r', encoding='utf-8').read()
old = """        private static FrameworkElement FindByName(System.Windows.DependencyObject root, string name)
        {
            if (root is FrameworkElement fe && fe.Name == name) return fe;
            int count = System.Windows.Media.VisualTreeHelper.GetChildrenCount(root);
            for (int i = 0; i < count; i++)
            {
                var r = FindByName(System.Windows.Media.VisualTreeHelper.GetChild(root, i), name);
                if (r != null) return r;
            }
            return null;
        }"""
new = """        private static FrameworkElement FindByName(System.Windows.DependencyObject root, string name)
        {
            if (root is FrameworkElement fe)
            {
                if (fe.Name == name) return fe;
                try
                {
                    var f = fe.FindName(name) as FrameworkElement;
                    if (f != null) return f;
                }
                catch { }
            }
            int count = System.Windows.Media.VisualTreeHelper.GetChildrenCount(root);
            for (int i = 0; i < count; i++)
            {
                var r = FindByName(System.Windows.Media.VisualTreeHelper.GetChild(root, i), name);
                if (r != null) return r;
            }
            return null;
        }"""
assert old in t, 'FindByName anchor NOT FOUND'
t = t.replace(old, new, 1)
io.open(csfp, 'w', encoding='utf-8', newline='').write(t)
print('FindByName upgraded with FindName (NameScope)')
