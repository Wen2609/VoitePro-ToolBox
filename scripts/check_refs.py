# -*- coding: utf-8 -*-
import io, re, sys
import xml.parsers.expat
sys.stdout.reconfigure(encoding='utf-8')

xaml_path = r'D:\doubao space\VioletToolBox\VioletToolBox\MainWindow.xaml'
c = io.open(xaml_path, 'r', encoding='utf-8').read()
lines = c.split('\n')

VIEW_NAMES = ["HomeView","ScreenMirrorView","BasicFlashView","FastbootVisualizationView",
    "HiddenEnvironmentView","AboutToolView","SystemZoneView","OujiaFlashView","AutorootView",
    "AppManagementView","AndroidGeneralView","PayloadView","RomDownloadview","EdlFlashView",
    "ColorOSAssistantView","BackupAssistantView","VioletDownloadView"]

# 复用 expat 解析出 View 边界
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
p = P()
parser = xml.parsers.expat.ParserCreate(); parser.buffer_text = True
p.p = parser
parser.StartElementHandler = p.start; parser.EndElementHandler = p.end
parser.Parse(c, True)
view_blocks = p.views  # name -> (start_line, end_line)

# Window.Resources keys: L23-413
wr_block = '\n'.join(lines[22:412])
wr_keys = set(re.findall(r'x:Key\s*=\s*"([^"]+)"', wr_block))

# 各 View 局部 keys + StaticResource 引用
view_local_keys = {}
view_refs = {}
for nm, (s, e) in view_blocks.items():
    block = '\n'.join(lines[s-1:e])
    local = set(re.findall(r'x:Key\s*=\s*"([^"]+)"', block))
    view_local_keys[nm] = local
    refs = set(re.findall(r'(?:StaticResource|DynamicResource)\s+([A-Za-z0-9_.{}]+)', block))
    # 去掉 {x:Type Button} 之类
    refs = {r for r in refs if not r.startswith('{x:Type')}
    view_refs[nm] = refs

print('=== unresolved refs per view (not in own local, not in Window.Resources) ===')
for nm in VIEW_NAMES:
    if nm not in view_blocks: continue
    own = view_local_keys[nm]
    un = view_refs[nm] - own - wr_keys
    if un:
        print(f'{nm}: {sorted(un)}')
print('=== done ===')
