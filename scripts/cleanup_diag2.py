# -*- coding: utf-8 -*-
import io, re, sys
sys.stdout.reconfigure(encoding='utf-8')
csfp = r'D:\doubao space\VioletToolBox\VioletToolBox\MainWindow.xaml.cs'
t = io.open(csfp, 'r', encoding='utf-8').read()
out = []

# 1) 移除 ctor 外层 try {（wrap_ctor 加的）
old = """        public MainWindow()
        {
            try
            {
            // 性能：冻结静态 Freezable 资源"""
new = """        public MainWindow()
        {
            // 性能：冻结静态 Freezable 资源"""
if old in t:
    t = t.replace(old, new, 1)
    out.append('ctor outer try removed')
else:
    out.append('ctor outer try NOT FOUND')

# 2) 移除 ctor catch 块
old2 = """            InitializeLanguageUi();
            try { System.IO.File.AppendAllText(System.IO.Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "startup.log"), "ctor end\\r\\n"); } catch { }
            }
            catch (Exception _ctorEx)
            {
                try { System.IO.File.AppendAllText(System.IO.Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "startup.log"), "CTOR EX: " + _ctorEx + "\\r\\n"); } catch { }
            }"""
new2 = """            InitializeLanguageUi();"""
if old2 in t:
    t = t.replace(old2, new2, 1)
    out.append('ctor catch removed')
else:
    out.append('ctor catch NOT FOUND')

# 3) 移除 m1-m7 日志 + check15s timer
t = re.sub(r'            try \{ System\.IO\.File\.AppendAllText\(System\.IO\.Path\.Combine\(AppDomain\.CurrentDomain\.BaseDirectory, "startup\.log"\), "m\d[^"]*"\); \} catch \{ \}\n', '', t)
out.append('m marks removed')
old3 = """            System.Windows.Application.Current.Dispatcher.BeginInvoke(new System.Action(() =>
            {
                var _chk = new System.Threading.Timer((_s) =>
                {
                    try
                    {
                        System.Windows.Application.Current.Dispatcher.Invoke(() =>
                        {
                            System.IO.File.AppendAllText(System.IO.Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "startup.log"),
                                "check15s visible=" + this.IsVisible + " state=" + this.WindowState + " visProp=" + this.Visibility + "\\r\\n");
                        });
                    }
                    catch { }
                }, null, 15000, System.Threading.Timeout.Infinite);
            }));
        }"""
new3 = """        }"""
if old3 in t:
    t = t.replace(old3, new3, 1)
    out.append('check15s timer removed')
else:
    out.append('check15s NOT FOUND')

# 4) 移除 show-flow 诊断（ctor end / source init / loaded fired）
t = re.sub(r'            try \{ System\.IO\.File\.AppendAllText\(System\.IO\.Path\.Combine\(AppDomain\.CurrentDomain\.BaseDirectory, "startup\.log"\), "ctor end\\r\\n"\); \} catch \{ \}\n', '', t)
t = t.replace("""            this.SourceInitialized += (s, e) => { try { System.IO.File.AppendAllText(System.IO.Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "startup.log"), "source init\\r\\n"); } catch { } };
""", '')
old4 = """            try { System.IO.File.AppendAllText(System.IO.Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "startup.log"), "loaded fired visible=" + this.IsVisible + "\\r\\n"); } catch { }
"""
if old4 in t:
    t = t.replace(old4, '', 1)
    out.append('show-flow diag removed')
else:
    out.append('loaded fired NOT FOUND')

# 5) InstantiatePage 的 LC 日志（before/after/EX）
old5 = """                try { System.IO.File.AppendAllText(System.IO.Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "startup.log"), "LC " + viewName + " before\\r\\n"); } catch { }
                var r = dt.LoadContent() as FrameworkElement;
                try { System.IO.File.AppendAllText(System.IO.Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "startup.log"), "LC " + viewName + " after\\r\\n"); } catch { }
                return r;
            }
            catch (Exception _lcex)
            {
                try { System.IO.File.AppendAllText(System.IO.Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "startup.log"), "LC " + viewName + " EX: " + _lcex.GetType().Name + ": " + _lcex.Message + "\\r\\n"); } catch { }
                return null;
            }"""
new5 = """                return dt.LoadContent() as FrameworkElement;
            }
            catch { return null; }"""
if old5 in t:
    t = t.replace(old5, new5, 1)
    out.append('LC logs removed')
else:
    out.append('LC logs NOT FOUND')

io.open(csfp, 'w', encoding='utf-8', newline='').write(t)
print('\n'.join(out))

# 6) 删除诊断脚本产物
import os
for f in ['stack2.txt', 'stack3.txt', 'stack4.txt', 'autoroot_body.txt', 'autoroot_tpl_backup.xaml', 'hang.dmp']:
    p = os.path.join(r'D:\doubao space\VioletToolBox', f)
    if os.path.exists(p):
        os.remove(p)
        print('removed', f)
