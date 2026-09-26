# -*- coding: utf-8 -*-
import io, sys
sys.stdout.reconfigure(encoding='utf-8')
fp = r'D:\doubao space\VioletToolBox\VioletToolBox\MainWindow.xaml.cs'
t = io.open(fp, 'r', encoding='utf-8').read()
old = """        public MainWindow()
        {
            // 性能：冻结静态 Freezable 资源（画刷/效果），减少渲染时资源切换开销
            try
            {
                FreezeAllFreezables(this.Resources);
                FreezeAllFreezables(System.Windows.Application.Current?.Resources);
            }
            catch { }"""
new = """        public MainWindow()
        {
            try
            {
            // 性能：冻结静态 Freezable 资源（画刷/效果），减少渲染时资源切换开销
            try
            {
                FreezeAllFreezables(this.Resources);
                FreezeAllFreezables(System.Windows.Application.Current?.Resources);
            }
            catch { }"""
assert old in t, 'ctor open anchor NOT FOUND'
t = t.replace(old, new, 1)

# 构造函数结尾（InitializeLanguageUi 后）加 catch
old_end = """            InitializeLanguageUi();
            try { System.IO.File.AppendAllText(System.IO.Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "startup.log"), "ctor end\\r\\n"); } catch { }"""
new_end = """            InitializeLanguageUi();
            try { System.IO.File.AppendAllText(System.IO.Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "startup.log"), "ctor end\\r\\n"); } catch { }
            }
            catch (Exception _ctorEx)
            {
                try { System.IO.File.AppendAllText(System.IO.Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "startup.log"), "CTOR EX: " + _ctorEx + "\\r\\n"); } catch { }
            }"""
assert old_end in t, 'ctor end anchor NOT FOUND'
t = t.replace(old_end, new_end, 1)
io.open(fp, 'w', encoding='utf-8', newline='').write(t)
print('ctor try/catch added')
