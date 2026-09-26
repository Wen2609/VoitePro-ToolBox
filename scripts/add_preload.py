# -*- coding: utf-8 -*-
import io, sys
sys.stdout.reconfigure(encoding='utf-8')
fp = r'D:\doubao space\VioletToolBox\VioletToolBox\MainWindow.EdlFlash.cs'
t = io.open(fp, 'r', encoding='utf-8').read()
old = """            // 延迟 EDL 引擎初始化到窗口显示后，避免 WMI 端口枚举阻塞启动（懒加载下此初始化不依赖首帧）
            System.Windows.Application.Current?.Dispatcher.BeginInvoke(
                new System.Action(InitializeEdlEngine),
                System.Windows.Threading.DispatcherPriority.Background);
        }"""
new = """            // 延迟 EDL 引擎初始化到窗口显示后，避免 WMI 端口枚举阻塞启动（懒加载下此初始化不依赖首帧）
            System.Windows.Application.Current?.Dispatcher.BeginInvoke(
                new System.Action(InitializeEdlEngine),
                System.Windows.Threading.DispatcherPriority.Background);
            // 后台预加载全部 16 个页面（窗口显示后，Background 优先级），页面切换秒开
            System.Windows.Application.Current?.Dispatcher.BeginInvoke(new System.Action(async () =>
            {
                await System.Threading.Tasks.Task.Delay(600);
                foreach (var key in _pageTemplateKeys)
                {
                    var vn2 = key.StartsWith("Page_") ? key.Substring("Page_".Length) : key;
                    if (!_pageInstances.ContainsKey(vn2))
                    {
                        var inst = InstantiatePage(vn2);
                        if (inst != null) _pageInstances[vn2] = inst;
                    }
                }
            }), System.Windows.Threading.DispatcherPriority.Background);
        }"""
assert old in t, 'OnInitialized anchor NOT FOUND'
t = t.replace(old, new, 1)
io.open(fp, 'w', encoding='utf-8', newline='').write(t)
print('background preload of all pages added')
