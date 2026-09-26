# -*- coding: utf-8 -*-
import io, sys
sys.stdout.reconfigure(encoding='utf-8')
fp = r'D:\doubao space\VioletToolBox\VioletToolBox\MainWindow.xaml.cs'
t = io.open(fp, 'r', encoding='utf-8').read()

# 1) 构造函数尾（InitializeLanguageUi 后）写 ctor end
old1 = """            InitializeLanguageUi();
        }


        private static readonly System.Collections.Generic.Dictionary<string, string> _nameViewMapStatic0"""
new1 = """            InitializeLanguageUi();
            try { System.IO.File.AppendAllText(System.IO.Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "startup.log"), "ctor end\\r\\n"); } catch { }
        }


        private static readonly System.Collections.Generic.Dictionary<string, string> _nameViewMapStatic0"""
assert old1 in t, 'anchor1 NOT FOUND'
t = t.replace(old1, new1, 1)

# 2) Loaded 处理器头写 loaded fired + 10s 后查可见性
old2 = """        private void MainWindow_Loaded(object sender, RoutedEventArgs e)
        {
            var homeItem = this.FindControlInPages("HomeButton") as HandyControl.Controls.SideMenuItem;"""
new2 = """        private void MainWindow_Loaded(object sender, RoutedEventArgs e)
        {
            try { System.IO.File.AppendAllText(System.IO.Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "startup.log"), "loaded fired visible=" + this.IsVisible + "\\r\\n"); } catch { }
            var homeItem = this.FindControlInPages("HomeButton") as HandyControl.Controls.SideMenuItem;"""
assert old2 in t, 'anchor2 NOT FOUND'
t = t.replace(old2, new2, 1)

# 3) SourceInitialized 写日志
old3 = """            this.Loaded += MainWindow_Loaded;
            this.Activated += (s, e) => ClearScrcpyWindowTopMost();"""
new3 = """            this.Loaded += MainWindow_Loaded;
            this.SourceInitialized += (s, e) => { try { System.IO.File.AppendAllText(System.IO.Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "startup.log"), "source init\\r\\n"); } catch { } };
            this.Activated += (s, e) => ClearScrcpyWindowTopMost();"""
assert old3 in t, 'anchor3 NOT FOUND'
t = t.replace(old3, new3, 1)

# 4) Dispatcher 15s 后检查可见性
old4 = """            InitializeLanguageUi();
            try { System.IO.File.AppendAllText(System.IO.Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "startup.log"), "ctor end\\r\\n"); } catch { }
        }"""
new4 = """            InitializeLanguageUi();
            try { System.IO.File.AppendAllText(System.IO.Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "startup.log"), "ctor end\\r\\n"); } catch { }
            System.Windows.Application.Current.Dispatcher.BeginInvoke(new System.Action(() =>
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
assert old4 in t, 'anchor4 NOT FOUND'
t = t.replace(old4, new4, 1)

io.open(fp, 'w', encoding='utf-8', newline='').write(t)
print('show-flow diagnostics added')
