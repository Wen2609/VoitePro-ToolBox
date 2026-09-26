# -*- coding: utf-8 -*-
import io, sys, os
sys.stdout.reconfigure(encoding='utf-8')
base = r'D:\doubao space\VioletToolBox\VioletToolBox'

# 1) 删除 EDL 相关 cs 文件
to_del = ['MainWindow.EdlFlash.cs', 'MainWindow.EdlSession.cs', 'MainWindow.EdlDynamicSuper.cs',
          'MainWindow.EdlFeedback.cs', 'EdlBuildPropReader.cs']
for f in to_del:
    p = os.path.join(base, f)
    if os.path.exists(p):
        os.remove(p)
        print('deleted', f)

# 2) csproj 移除 SharpEDL
cpp = os.path.join(base, 'SmartTool.csproj')
c = io.open(cpp, 'r', encoding='utf-8').read()
if '<PackageReference Include="SharpEDL"' in c:
    c = c.replace('<PackageReference Include="SharpEDL" Version="1.0.4" />\r\n', '')
    c = c.replace('<PackageReference Include="SharpEDL" Version="1.0.4" />\n', '')
    io.open(cpp, 'w', encoding='utf-8', newline='').write(c)
    print('SharpEDL removed from csproj')
else:
    print('SharpEDL not in csproj')

# 3) xaml.cs 加 OnInitialized（若不存在）
csfp = os.path.join(base, 'MainWindow.xaml.cs')
cs = io.open(csfp, 'r', encoding='utf-8').read()
if 'protected override void OnInitialized' not in cs:
    anchor = '        public MainWindow()'
    oninit = """        protected override void OnInitialized(EventArgs e)
        {
            base.OnInitialized(e);
            CollectPageTemplateKeys();
            // 后台预加载全部页面：后台线程延迟 3s（窗口已显示）后，按页在 Background 优先级逐页实例化，
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
        }

"""
    assert anchor in cs, 'ctor anchor NOT FOUND'
    cs = cs.replace(anchor, oninit + anchor, 1)
    io.open(csfp, 'w', encoding='utf-8', newline='').write(cs)
    print('OnInitialized added to MainWindow.xaml.cs')
else:
    print('OnInitialized already exists in xaml.cs')
