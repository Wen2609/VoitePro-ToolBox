# -*- coding: utf-8 -*-
import io, sys
sys.stdout.reconfigure(encoding='utf-8')
fp = r'D:\doubao space\VioletToolBox\VioletToolBox\MainWindow.xaml.cs'
t = io.open(fp, 'r', encoding='utf-8').read()

# 1) helper 区：加 _pageTemplateKeys + CollectPageTemplateKeys
old = """        // ===== 懒加载页面支持（2026-09 性能重构） =====
        private readonly Dictionary<string, FrameworkElement> _pageInstances = new Dictionary<string, FrameworkElement>();
        private string _currentPage = "HomeView";
        private ContentControl _pageHost;"""
new = """        // ===== 懒加载页面支持（2026-09 性能重构） =====
        private readonly Dictionary<string, FrameworkElement> _pageInstances = new Dictionary<string, FrameworkElement>();
        private readonly List<string> _pageTemplateKeys = new List<string>();
        private string _currentPage = "HomeView";
        private ContentControl _pageHost;

        private void CollectPageTemplateKeys()
        {
            foreach (var key in this.Resources.Keys)
            {
                if (key is string s && s.StartsWith("Page_") && !_pageTemplateKeys.Contains(s))
                    _pageTemplateKeys.Add(s);
            }
        }"""
assert old in t, 'helper anchor NOT FOUND'
t = t.replace(old, new, 1)

# 2) FindControlInPages：找不到时按需实例化页面
old2 = """        /// <summary>在已实例化的页面（当前宿主 + 缓存实例）视觉树中按 x:Name 查找控件</summary>
        private object FindControlInPages(string name)
        {
            if (_pageHost != null)
            {
                var f = FindByName(_pageHost, name);
                if (f != null) return f;
            }
            foreach (var inst in _pageInstances.Values)
            {
                var f = FindByName(inst, name);
                if (f != null) return f;
            }
            return null;
        }"""
new2 = """        /// <summary>在已实例化页面（当前宿主 + 缓存实例）中按 x:Name 查找；找不到时按需实例化未加载页面再查（懒加载兼容）</summary>
        private object FindControlInPages(string name)
        {
            if (_pageHost != null)
            {
                var f = FindByName(_pageHost, name);
                if (f != null) return f;
            }
            foreach (var inst in _pageInstances.Values)
            {
                var f = FindByName(inst, name);
                if (f != null) return f;
            }
            foreach (var key in _pageTemplateKeys)
            {
                if (_pageInstances.ContainsKey(key)) continue;
                var inst = InstantiatePage(key);
                if (inst == null) continue;
                _pageInstances[key] = inst;
                var f2 = FindByName(inst, name);
                if (f2 != null) return f2;
            }
            return null;
        }"""
assert old2 in t, 'FindControlInPages anchor NOT FOUND'
t = t.replace(old2, new2, 1)

# 3) 构造函数 InitializeComponent 后收集模板 key
old3 = """            InitializeComponent();
            try { System.IO.File.AppendAllText(System.IO.Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "startup.log"), $"{System.DateTime.Now:HH:mm:ss.fff} InitializeComponent done: {_swStart.ElapsedMilliseconds}ms\\r\\n"); } catch { }"""
new3 = """            InitializeComponent();
            CollectPageTemplateKeys();
            try { System.IO.File.AppendAllText(System.IO.Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "startup.log"), $"{System.DateTime.Now:HH:mm:ss.fff} InitializeComponent done: {_swStart.ElapsedMilliseconds}ms\\r\\n"); } catch { }"""
assert old3 in t, 'ctor anchor NOT FOUND'
t = t.replace(old3, new3, 1)

io.open(fp, 'w', encoding='utf-8', newline='').write(t)
print('helper upgraded: CollectPageTemplateKeys + FindControlInPages lazy-instantiate + ctor collect')
