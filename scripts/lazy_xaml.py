# -*- coding: utf-8 -*-
"""懒加载重构 v3：插入模板后重新解析定位 HomeView 闭标签"""
import io, re, sys
import xml.parsers.expat
sys.stdout.reconfigure(encoding='utf-8')

XAML = r'D:\doubao space\VioletToolBox\VioletToolBox\MainWindow.xaml'
raw = io.open(XAML, 'r', encoding='utf-8').read()
c = raw.replace('\r\n', '\n')
lines = c.split('\n')

VIEW_NAMES = ["HomeView","ScreenMirrorView","BasicFlashView","FastbootVisualizationView",
    "HiddenEnvironmentView","AboutToolView","SystemZoneView","OujiaFlashView","AutorootView",
    "AppManagementView","AndroidGeneralView","PayloadView","RomDownloadview","EdlFlashView",
    "ColorOSAssistantView","BackupAssistantView","VioletDownloadView"]
LAZY = [n for n in VIEW_NAMES if n != 'HomeView']

class P:
    def __init__(self):
        self.stack = []
        self.views = {}
    def start(self, tag, attrs):
        ln = self.p.CurrentLineNumber
        nm = attrs.get('x:Name') or attrs.get('Name')
        self.stack.append((tag, nm, ln))
    def end(self, tag):
        t, nm, ln = self.stack.pop()
        if t == 'Grid' and nm in VIEW_NAMES:
            self.views[nm] = (ln, self.p.CurrentLineNumber)

def parse(text):
    p = P()
    parser = xml.parsers.expat.ParserCreate(); parser.buffer_text = True
    p.p = parser
    parser.StartElementHandler = p.start; parser.EndElementHandler = p.end
    parser.Parse(text, True)
    return p.views

view_blocks = parse(c)
print('blocks:', len(view_blocks))

# ---- 1. 删除 16 个 View 块 ----
lazy_lines = [view_blocks[n] for n in LAZY]
del_start = min(s for s, e in lazy_lines) - 1
del_end = max(e for s, e in lazy_lines)
lines2 = lines[:del_start] + lines[del_end:]
c2 = '\n'.join(lines2)
print(f'removed L{del_start+1}-L{del_end}')

# ---- 2. FastbootCardGroupBoxStyle ----
fs, fe = view_blocks['FastbootVisualizationView']
fv_block = '\n'.join(lines[fs-1:fe])
m = re.search(r'<Style x:Key="FastbootCardGroupBoxStyle".*?</Style>', fv_block, re.DOTALL)
if not m:
    m = re.search(r'<Style x:Key="FastbootCardGroupBoxStyle"[^>]*/>', fv_block)
promoted = m.group(0) if m else None
print('promoted:', bool(promoted))

# ---- 3. DataTemplate 定义 ----
tpl_parts = []
if promoted:
    tpl_parts.append('                <!-- 跨View共享：FastbootCardGroupBoxStyle（HiddenEnvironment 引用） -->')
    tpl_parts.append('                ' + promoted)
tpl_parts.append('                <!-- 懒加载页面模板：首次实例化才构建视觉树（加速启动） -->')
IND = '                '
for name in LAZY:
    s, e = view_blocks[name]
    block = lines[s-1:e]
    tpl_parts.append(f'{IND}<DataTemplate x:Key="Page_{name}">')
    tpl_parts += block
    tpl_parts.append(f'{IND}</DataTemplate>')
tpl_str = '\n'.join(tpl_parts) + '\n'

# ---- 4. 插入模板到 </FrameworkElement.Resources> 前 ----
marker = '</FrameworkElement.Resources>'
pos = c2.find(marker)
assert pos > 0, 'marker not found'
c3 = c2[:pos] + tpl_str + c2[pos:]
print('templates inserted, c3 lines:', c3.count('\n')+1)

# ---- 5. 重新解析 c3，定位 HomeView 闭标签，插入 PageHost ----
vb3 = parse(c3)
print('c3 views:', {k: vb3[k] for k in vb3 if k in ('HomeView',)})
home_start, home_end = vb3['HomeView']
c3_lines = c3.split('\n')
# home_end 是 1-based 闭标签行 → 0-based index = home_end-1
pagehost = [
    '                    <!-- 懒加载页面宿主：16 个功能页按需实例化（Page_<ViewName> 模板） -->',
    '                    <ContentControl x:Name="PageHost" HorizontalContentAlignment="Stretch" VerticalContentAlignment="Stretch"/>'
]
c4_lines = c3_lines[:home_end] + pagehost + c3_lines[home_end:]
c4 = '\n'.join(c4_lines)
io.open(XAML, 'w', encoding='utf-8', newline='').write(c4.replace('\n', '\r\n'))
print('written. c4 lines:', len(c4_lines), '(original', len(lines), ')')
