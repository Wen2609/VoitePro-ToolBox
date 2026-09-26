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
view_blocks = p.views

wr_block = '\n'.join(lines[22:412])
wr_keys = set(re.findall(r'x:Key\s*=\s*"([^"]+)"', wr_block))

# 定位每个 key 的定义位置
def where(key):
    if key in wr_keys: return 'Window.Resources'
    for nm, (s, e) in view_blocks.items():
        block = '\n'.join(lines[s-1:e])
        if re.search(r'x:Key\s*=\s*"' + re.escape(key) + r'"', block):
            return f'{nm} (L{s}-{e})'
    return '??? NOT FOUND'

# 跨 View 引用的候选 key
candidates = ['PayloadGroupBoxStyle','FastbootCardGroupBoxStyle','EdlCardGroupBoxStyle',
    'EdlPartitionCellStyle','EdlPartitionTextStyle','FastbootPartitionTextCellStyle',
    'OugaFlashCardGroupBoxStyle','RomSectionStyle','RomVersionDropDownItemStyle',
    'ColorOSLogGroupBoxStyle','ColorOSCenteredDataTextStyle','ColorOSColumnHeaderStyle',
    'ColorOSLeftColumnHeaderStyle','ColorOSLeftDataTextStyle','FastbootButtonBaseStyle',
    'StorageGradient','MemoryGradient','DropShadowEffect','PageCard','PageTitle',
    'PagePrimaryButton','PageSecondaryButton','PageLabel','PageTextBox','PageComboBox',
    'PageCheckBox','PageSwitch','PageLightButton','PageProgress','PageSubtitle',
    'TextSecondaryBrush','TextTertiaryBrush','CardContainer','HeroCard','GhostButton',
    'WhiteButton','ActionCardButton','BackgroundBrush','ToggleSwitch','PageLabelCtl',
    'PageComboBoxItem','BoolToVisibilityConverter','ProgressBarIndicatorWidthConverter']

for k in candidates:
    print(f'{k}: {where(k)}')
