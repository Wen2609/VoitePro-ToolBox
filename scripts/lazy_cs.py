# -*- coding: utf-8 -*-
"""cs 改造：懒加载支持。1) 收集模板内部控件名 2) 替换页面级 FindName 块 3) 替换控件 FindName"""
import io, re, sys
import xml.parsers.expat
sys.stdout.reconfigure(encoding='utf-8')

XAML = r'D:\doubao space\VioletToolBox\VioletToolBox\MainWindow.xaml'
CS = r'D:\doubao space\VioletToolBox\VioletToolBox\MainWindow.xaml.cs'

# ---- 收集 DataTemplate 内部控件的 x:Name（16 个模板页）----
c = io.open(XAML, 'r', encoding='utf-8').read()
# 模板区域：<!-- 懒加载页面模板 --> 到 </FrameworkElement.Resources>
tpl_region = c.split('懒加载页面模板', 1)[1].split('</FrameworkElement.Resources>', 1)[0]
inner_names = set(re.findall(r'(?:x:Name|Name)\s*=\s*"([^"]+)"', tpl_region))
print('template inner names:', len(inner_names))

# 主 XAML 外壳保留区（<FrameworkElement.Resources> 前 + HomeView 等）
outer_names = set(re.findall(r'(?:x:Name|Name)\s*=\s*"([^"]+)"', c.split('懒加载页面模板', 1)[0]))
# 移除模板内重复
outer_only = outer_names - inner_names
print('outer names:', len(outer_only))

# ---- cs 处理 ----
cs = io.open(CS, 'r', encoding='utf-8').read()
orig = cs

# ---- A. 页面级 FindName+Visibility 块替换为 ShowPage ----
# 模式：17 个 FindName 行块
fn_re = re.compile(
    r'var homeView = this\.FindName\("HomeView"\) as Grid;\n'
    r'(?:.*?)\n'
    r'\s*var violetDownloadView = this\.FindName\("VioletDownloadView"\) as Grid;',
    re.DOTALL)
# Visibility 块：if (homeView != null) ... if (violetDownloadView != null) ...
vis_re = re.compile(
    r'if \(homeView != null\) homeView\.Visibility = Visibility\.(\w+);\n'
    r'(?:.*?)\n'
    r'\s*if \(violetDownloadView != null\) violetDownloadView\.Visibility = Visibility\.\w+;',
    re.DOTALL)

VAR2VIEW = {
    'homeView':'HomeView','screenMirrorView':'ScreenMirrorView','basicFlashView':'BasicFlashView',
    'fastbootVisualizationView':'FastbootVisualizationView','hiddenEnvironmentView':'HiddenEnvironmentView',
    'aboutToolView':'AboutToolView','systemZoneView':'SystemZoneView','oujiaFlashView':'OujiaFlashView',
    'autorootView':'AutorootView','appManagementView':'AppManagementView','androidGeneralView':'AndroidGeneralView',
    'payloadView':'PayloadView','romDownloadView':'RomDownloadview','edlFlashView':'EdlFlashView',
    'colorOSAssistantView':'ColorOSAssistantView','backupAssistantView':'BackupAssistantView',
    'violetDownloadView':'VioletDownloadView',
}

def replace_show_blocks(text):
    # 找所有 Visibility 块 → 提取哪个 View Visible
    vis_blocks = list(vis_re.finditer(text))
    print('visibility blocks found:', len(vis_blocks))
    if not vis_blocks:
        return text, 0
    new_text = text
    for m in reversed(vis_blocks):
        # 找 Visibility = Visibility.Visible 的那一行（每个方法只有一页 Visible）
        vm = None
        for line in m.group(0).split('\n'):
            mm = re.match(r'if \((\w+) != null\) \1\.Visibility = Visibility\.(\w+);', line.strip())
            if mm and mm.group(2) == 'Visible':
                vm = mm; break
        if not vm: continue
        view = VAR2VIEW.get(vm.group(1))
        if not view: continue
        repl = f'ShowPage("{view}");'
        new_text = new_text[:m.start()] + repl + new_text[m.end():]
    return new_text, len(vis_blocks)

cs, n_vis = replace_show_blocks(cs)

# FindName 块替换（如果还在——Visibility 块替换后 FindName 块可能残留，一并清掉）
def remove_findname_blocks(text):
    blocks = list(fn_re.finditer(text))
    if not blocks:
        return text, 0
    new_text = text
    for m in reversed(blocks):
        new_text = new_text[:m.start()] + '' + new_text[m.end():]
    return new_text, len(blocks)

cs, n_fn = remove_findname_blocks(cs)
print('findname blocks removed:', n_fn)

# ---- B. 控件级 FindName 替换（模板内部控件 → FindControlInPages）----
# 外壳控件保留名单：主 XAML 外壳（含 HomeView）的所有 x:Name + 明确外壳控件
keep = outer_only
print('keep count:', len(keep))

count = 0
def repl_findname(m):
    global count
    name = m.group(1)
    if name in keep:
        return m.group(0)  # 保留 this.FindName
    count += 1
    return f'this.FindControlInPages("{name}")'

# 匹配 this.FindName("X")（含 as T 后缀不动）
cs2 = re.sub(r'this\.FindName\("([^"]+)"\)', repl_findname, cs)
print('control FindName replaced:', count)

# ---- C. 注入 helper 方法 + 字段 ----
helper = r'''
        // ===== 懒加载页面支持（2026-09 性能重构） =====
        private readonly Dictionary<string, FrameworkElement> _pageInstances = new Dictionary<string, FrameworkElement>();
        private string _currentPage = "HomeView";
        private ContentControl _pageHost;

        private void ShowPage(string viewName)
        {
            if (_pageHost == null)
                _pageHost = this.FindName("PageHost") as ContentControl;
            if (_pageHost == null) return;

            FrameworkElement page;
            if (viewName == "HomeView")
            {
                page = this.FindName("HomeView") as FrameworkElement;
            }
            else if (!_pageInstances.TryGetValue(viewName, out page))
            {
                page = InstantiatePage(viewName);
                if (page != null) _pageInstances[viewName] = page;
            }
            if (page == null) return;
            _currentPage = viewName;
            _pageHost.Content = page;
        }

        private FrameworkElement InstantiatePage(string viewName)
        {
            try
            {
                var dt = this.FindResource("Page_" + viewName) as DataTemplate;
                if (dt == null) return null;
                var tmp = new ContentControl { ContentTemplate = dt, Content = new object() };
                tmp.ApplyTemplate();
                var cp = FindVisualChild<ContentPresenter>(tmp);
                if (cp != null && System.Windows.Media.VisualTreeHelper.GetChildrenCount(cp) > 0)
                    return System.Windows.Media.VisualTreeHelper.GetChild(cp, 0) as FrameworkElement;
                return null;
            }
            catch { return null; }
        }

        /// <summary>在已实例化的页面（当前宿主 + 缓存实例）视觉树中按 x:Name 查找控件</summary>
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
        }

        private static FrameworkElement FindByName(System.Windows.DependencyObject root, string name)
        {
            if (root is FrameworkElement fe && fe.Name == name) return fe;
            int count = System.Windows.Media.VisualTreeHelper.GetChildrenCount(root);
            for (int i = 0; i < count; i++)
            {
                var r = FindByName(System.Windows.Media.VisualTreeHelper.GetChild(root, i), name);
                if (r != null) return r;
            }
            return null;
        }


'''

# 注入位置：MainWindow_Loaded 前（FreezeOne helper 之前）
anchor = '        private static void FreezeOne(System.Windows.Freezable f)'
assert anchor in cs2, 'anchor not found'
cs2 = cs2.replace(anchor, helper + '\n' + anchor, 1)

# ---- D. 构造函数：删 17 个 FindName 初始化（若还在）+ 初始 ShowPage ----
ctor_vis = re.search(
    r'// 初始化时显示首页视图，隐藏其他视图\n'
    r'var homeView = this\.FindName\("HomeView"\) as Grid;\n'
    r'.*?if \(violetDownloadView != null\) violetDownloadView\.Visibility = Visibility\.Collapsed;',
    cs2, re.DOTALL)
if ctor_vis:
    cs2 = cs2[:ctor_vis.start()] + '            // 懒加载：首屏显示 Home（其余页面首次切换时实例化）\n            ShowPage("HomeView");' + cs2[ctor_vis.end():]
    print('ctor init replaced')
else:
    print('WARN: ctor init block not found (maybe already replaced)')

# ---- E. HomeView 初始显示（构造函数 FindName("HomeView") as Grid 删除后）----
# 构造函数里 UpdateButtonStates("Home") 前的 ShowPage 已加。HomeButton_Click 等仍引用 homeView 变量？

io.open(CS, 'w', encoding='utf-8', newline='').write(cs2)
print('cs written. size', len(orig), '->', len(cs2))
