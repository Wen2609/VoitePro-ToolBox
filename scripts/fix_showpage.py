# -*- coding: utf-8 -*-
import io, sys
sys.stdout.reconfigure(encoding='utf-8')
csfp = r'D:\doubao space\VioletToolBox\VioletToolBox\MainWindow.xaml.cs'
t = io.open(csfp, 'r', encoding='utf-8').read()
old = """            FrameworkElement page;
            if (viewName == "HomeView")
            {
                page = this.FindControlInPages("HomeView") as FrameworkElement;
            }
            else if (!_pageInstances.TryGetValue(viewName, out page))
            {
                page = InstantiatePage(viewName);
                if (page != null) _pageInstances[viewName] = page;
            }
            if (page == null) return;
            _currentPage = viewName;
            _pageHost.Content = page;"""
new = """            FrameworkElement page = null;
            if (viewName == "HomeView")
            {
                // HomeView 已在窗口主内容区（窗口树内），不能赋给 PageHost（双父冲突）；
                // 清空 PageHost 并显示 HomeView 即可
                _pageHost.Content = null;
                var home = this.FindControlInPages("HomeView") as FrameworkElement;
                if (home != null) home.Visibility = System.Windows.Visibility.Visible;
                _currentPage = viewName;
                return;
            }
            else if (!_pageInstances.TryGetValue(viewName, out page))
            {
                page = InstantiatePage(viewName);
                if (page != null) _pageInstances[viewName] = page;
            }
            if (page == null) return;
            var hv = this.FindControlInPages("HomeView") as FrameworkElement;
            if (hv != null) hv.Visibility = System.Windows.Visibility.Collapsed;
            _currentPage = viewName;
            _pageHost.Content = page;"""
assert old in t, 'ShowPage anchor NOT FOUND'
t = t.replace(old, new, 1)
io.open(csfp, 'w', encoding='utf-8', newline='').write(t)
print('ShowPage fixed (HomeView stays in window tree, PageHost only for lazy pages)')
