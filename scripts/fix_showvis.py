# -*- coding: utf-8 -*-
import io, sys
sys.stdout.reconfigure(encoding='utf-8')
csfp = r'D:\doubao space\VioletToolBox\VioletToolBox\MainWindow.xaml.cs'
t = io.open(csfp, 'r', encoding='utf-8').read()
old = """            if (page == null) return;
            var hv = this.FindControlInPages("HomeView") as FrameworkElement;
            if (hv != null) hv.Visibility = System.Windows.Visibility.Collapsed;
            _currentPage = viewName;
            _pageHost.Content = page;"""
new = """            if (page == null) return;
            var hv = this.FindControlInPages("HomeView") as FrameworkElement;
            if (hv != null) hv.Visibility = System.Windows.Visibility.Collapsed;
            _currentPage = viewName;
            _pageHost.Content = page;
            page.Visibility = System.Windows.Visibility.Visible;"""
assert old in t, 'ShowPage visibility anchor NOT FOUND'
t = t.replace(old, new, 1)
io.open(csfp, 'w', encoding='utf-8', newline='').write(t)
print('ShowPage sets page.Visibility=Visible')
