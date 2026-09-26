# -*- coding: utf-8 -*-
import io, sys
sys.stdout.reconfigure(encoding='utf-8')
fp = r'D:\doubao space\VioletToolBox\VioletToolBox\MainWindow.EdlFlash.cs'
t = io.open(fp, 'r', encoding='utf-8').read()
old = """            // 后台预加载全部 16 个页面（窗口显示后，Background 优先级），页面切换秒开
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
new = """            // 后台预加载全部页面：后台线程延迟 3s（窗口已显示）后，按页在 Background 优先级逐页实例化，
            // 每页之间消息循环可穿插渲染/输入，不阻塞界面响应，页面切换秒开
            var _preloadPages = new System.Collections.Generic.List<string>();
            foreach (var key in _pageTemplateKeys)
            {
                var vn2 = key.StartsWith("Page_") ? key.Substring("Page_".Length) : key;
                if (!_pageInstances.ContainsKey(vn2)) _preloadPages.Add(vn2);
            }
            if (_preloadPages.Count > 0)
            {
                var _dispatcher = System.Windows.Application.Current?.Dispatcher;
                if (_dispatcher != null)
                {
                    new System.Threading.Timer((_) =>
                    {
                        foreach (var vn2 in _preloadPages)
                        {
                            _dispatcher.BeginInvoke(new System.Action(() =>
                            {
                                if (!_pageInstances.ContainsKey(vn2))
                                {
                                    var inst = InstantiatePage(vn2);
                                    if (inst != null) _pageInstances[vn2] = inst;
                                }
                            }), System.Windows.Threading.DispatcherPriority.Background);
                        }
                    }, null, 3000, System.Threading.Timeout.Infinite);
                }
            }
        }"""
assert old in t, 'preload anchor NOT FOUND'
t = t.replace(old, new, 1)
io.open(fp, 'w', encoding='utf-8', newline='').write(t)
print('preload moved to background thread timer + per-page background dispatch')
