# -*- coding: utf-8 -*-
import io, re, sys
sys.stdout.reconfigure(encoding='utf-8')
csfp = r'D:\doubao space\VioletToolBox\VioletToolBox\MainWindow.xaml.cs'
t = io.open(csfp, 'r', encoding='utf-8').read()

# 1) 加 _instantiating 字段（放在 _pageInstances 声明后）
old_f = """        private readonly System.Collections.Generic.Dictionary<string, FrameworkElement> _pageInstances = new System.Collections.Generic.Dictionary<string, FrameworkElement>();"""
new_f = """        private readonly System.Collections.Generic.Dictionary<string, FrameworkElement> _pageInstances = new System.Collections.Generic.Dictionary<string, FrameworkElement>();
        private readonly System.Collections.Generic.HashSet<string> _instantiating = new System.Collections.Generic.HashSet<string>();"""
if old_f in t:
    t = t.replace(old_f, new_f, 1)
    print('field added')
else:
    print('field anchor NOT FOUND - try alt')
    alt = re.search(r'_pageInstances = new[^;]+;', t)
    if alt:
        t = t[:alt.end()] + '\n        private readonly System.Collections.Generic.HashSet<string> _instantiating = new System.Collections.Generic.HashSet<string>();' + t[alt.end():]
        print('field added (alt)')
    else:
        print('FIELD FAIL')

# 2) InstantiatePage 加重入保护
old_ip = """        private FrameworkElement InstantiatePage(string viewName)
        {
            try
            {
                var dt = this.FindResource("Page_" + viewName) as DataTemplate;
                if (dt == null) return null;"""
new_ip = """        private FrameworkElement InstantiatePage(string viewName)
        {
            if (!_instantiating.Add(viewName)) return null;
            try
            {
                var dt = this.FindResource("Page_" + viewName) as DataTemplate;
                if (dt == null) return null;"""
if old_ip in t:
    t = t.replace(old_ip, new_ip, 1)
    print('reentry guard start added')
else:
    print('InstantiatePage anchor NOT FOUND')

# 3) InstantiatePage 结束处（catch 前）加 finally 移除
old_ip2 = """                return r;
            }
            catch (Exception _lcex)
            {
                try { System.IO.File.AppendAllText(System.IO.Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "startup.log"), "LC " + viewName + " EX: " + _lcex.GetType().Name + ": " + _lcex.Message + "\\r\\n"); } catch { }
                return null;
            }
        }"""
new_ip2 = """                return r;
            }
            catch (Exception _lcex)
            {
                try { System.IO.File.AppendAllText(System.IO.Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "startup.log"), "LC " + viewName + " EX: " + _lcex.GetType().Name + ": " + _lcex.Message + "\\r\\n"); } catch { }
                return null;
            }
            finally
            {
                _instantiating.Remove(viewName);
            }
        }"""
if old_ip2 in t:
    t = t.replace(old_ip2, new_ip2, 1)
    print('reentry guard finally added')
else:
    print('InstantiatePage end anchor NOT FOUND')

io.open(csfp, 'w', encoding='utf-8', newline='').write(t)
print('done')
