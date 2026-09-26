# -*- coding: utf-8 -*-
import io, sys
import xml.parsers.expat
sys.stdout.reconfigure(encoding='utf-8')

xaml_path = r'D:\doubao space\VioletToolBox\VioletToolBox\MainWindow.xaml'
c = io.open(xaml_path, 'r', encoding='utf-8').read()

VIEW_NAMES = ["HomeView","ScreenMirrorView","BasicFlashView","FastbootVisualizationView",
    "HiddenEnvironmentView","AboutToolView","SystemZoneView","OujiaFlashView","AutorootView",
    "AppManagementView","AndroidGeneralView","PayloadView","RomDownloadview","EdlFlashView",
    "ColorOSAssistantView","BackupAssistantView","VioletDownloadView"]

class P:
    def __init__(self):
        self.stack = []
        self.views = {}
        self.errors = []
    def start(self, tag, attrs):
        ln = self.p.CurrentLineNumber
        nm = attrs.get('x:Name') or attrs.get('Name')
        self.stack.append((tag, nm, ln))
    def end(self, tag):
        if not self.stack:
            self.errors.append(f'extra close at line {self.p.CurrentLineNumber}: {tag}')
            return
        t, nm, ln = self.stack.pop()
        if t == 'Grid' and nm in VIEW_NAMES:
            self.views[nm] = (ln, self.p.CurrentLineNumber)

p = P()
parser = xml.parsers.expat.ParserCreate()
parser.buffer_text = True
p.p = parser
parser.StartElementHandler = p.start
parser.EndElementHandler = p.end
try:
    parser.Parse(c, True)
except Exception as e:
    print('PARSE ERROR:', e, 'line', parser.CurrentLineNumber)

print('open stack remaining:', len(p.stack))
print('errors:', p.errors[:3])
print('views found:', len(p.views))
for nm in VIEW_NAMES:
    if nm in p.views:
        s, e = p.views[nm]
        print(f'{nm}: L{s}-L{e} ({e-s} lines)')
    else:
        print(f'{nm}: NOT FOUND')
