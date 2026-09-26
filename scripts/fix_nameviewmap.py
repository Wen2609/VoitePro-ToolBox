# -*- coding: utf-8 -*-
import io, sys
sys.stdout.reconfigure(encoding='utf-8')
fp = r'D:\doubao space\VioletToolBox\VioletToolBox\MainWindow.xaml.cs'
t = io.open(fp, 'r', encoding='utf-8').read()

# 1) 加 _nameViewMap 字段
old = """        private readonly Dictionary<string, FrameworkElement> _pageInstances = new Dictionary<string, FrameworkElement>();
        private readonly List<string> _pageTemplateKeys = new List<string>();
        private string _currentPage = "HomeView";
        private ContentControl _pageHost;"""
new = """        private readonly Dictionary<string, FrameworkElement> _pageInstances = new Dictionary<string, FrameworkElement>();
        private readonly List<string> _pageTemplateKeys = new List<string>();
        private readonly Dictionary<string, string> _nameViewMap = new Dictionary<string, string>();
        private string _currentPage = "HomeView";
        private ContentControl _pageHost;"""
assert old in t, 'field anchor NOT FOUND'
t = t.replace(old, new, 1)

# 2) FindControlInPages 换映射版
old2 = """        /// <summary>在已实例化页面（当前宿主 + 缓存实例）中按 x:Name 查找；找不到时按需实例化未加载页面再查（懒加载兼容）</summary>
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
                var vn = key.StartsWith("Page_") ? key.Substring("Page_".Length) : key;
                if (_pageInstances.ContainsKey(vn)) continue;
                var inst = InstantiatePage(vn);
                if (inst == null) continue;
                _pageInstances[vn] = inst;
                var f2 = FindByName(inst, name);
                if (f2 != null) return f2;
            }
            return null;
        }"""
new2 = """        /// <summary>按 x:Name 查找控件；name→页面 映射命中时直接实例化目标页，避免逐个页面试探（懒加载兼容）</summary>
        private object FindControlInPages(string name)
        {
            if (_nameViewMap.TryGetValue(name, out var vn))
            {
                if (_pageInstances.TryGetValue(vn, out var inst0))
                    return FindByName(inst0, name);
                var inst1 = InstantiatePage(vn);
                if (inst1 == null) return null;
                _pageInstances[vn] = inst1;
                return FindByName(inst1, name);
            }
            if (_pageHost != null)
            {
                var f = FindByName(_pageHost, name);
                if (f != null) { _nameViewMap[name] = "HomeView"; return f; }
            }
            foreach (var kv in _pageInstances)
            {
                var f = FindByName(kv.Value, name);
                if (f != null) { _nameViewMap[name] = kv.Key; return f; }
            }
            foreach (var key in _pageTemplateKeys)
            {
                var vn2 = key.StartsWith("Page_") ? key.Substring("Page_".Length) : key;
                if (_pageInstances.ContainsKey(vn2)) continue;
                var inst = InstantiatePage(vn2);
                if (inst == null) continue;
                _pageInstances[vn2] = inst;
                var f2 = FindByName(inst, name);
                if (f2 != null) { _nameViewMap[name] = vn2; return f2; }
            }
            return null;
        }"""
assert old2 in t, 'FindControlInPages anchor NOT FOUND'
t = t.replace(old2, new2, 1)

io.open(fp, 'w', encoding='utf-8', newline='').write(t)
print('name→view map optimization applied')
