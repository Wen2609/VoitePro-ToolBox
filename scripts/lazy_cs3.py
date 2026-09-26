# -*- coding: utf-8 -*-
"""处理 partial 文件中的页面级 FindName+Visibility 块（18 变量版本，含 downloadView）"""
import io, re, sys, os
sys.stdout.reconfigure(encoding='utf-8')

ROOT = r'D:\doubao space\VioletToolBox\VioletToolBox'
FILES = ['MainWindow.HiddenEnvironment.cs', 'MainWindow.Payload.cs', 'MainWindow.ColorOSAssistant.cs',
         'MainWindow.BackupAssistant.cs', 'RomDownload.cs', 'oujiaflash.cs']

fn_re = re.compile(
    r'var homeView = this\.FindName\("HomeView"\) as Grid;\n'
    r'(?:.*?)\n'
    r'\s*var violetDownloadView = this\.FindName\("VioletDownloadView"\) as Grid;',
    re.DOTALL)

vis_re = re.compile(
    r'if \(homeView != null\) homeView\.Visibility = Visibility\.(\w+);\n'
    r'(?:.*?)\n'
    r'\s*if \(violetDownloadView != null\) violetDownloadView\.Visibility = Visibility\.\w+;',
    re.DOTALL)

VAR2VIEW = {
    'homeView':'HomeView','screenMirrorView':'ScreenMirrorView','basicFlashView':'BasicFlashView',
    'fastbootVisualizationView':'FastbootVisualizationView','hiddenEnvironmentView':'HiddenEnvironmentView',
    'downloadView':'DownloadView','aboutToolView':'AboutToolView','systemZoneView':'SystemZoneView',
    'oujiaFlashView':'OujiaFlashView','autorootView':'AutorootView','appManagementView':'AppManagementView',
    'androidGeneralView':'AndroidGeneralView','payloadView':'PayloadView','romDownloadView':'RomDownloadview',
    'edlFlashView':'EdlFlashView','colorOSAssistantView':'ColorOSAssistantView',
    'backupAssistantView':'BackupAssistantView','violetDownloadView':'VioletDownloadView',
}

total_vis = 0
total_fn = 0
for fname in FILES:
    fp = os.path.join(ROOT, fname)
    txt = io.open(fp, 'r', encoding='utf-8').read()
    new_txt = txt
    # 1. Visibility 块 → ShowPage
    vis_blocks = list(vis_re.finditer(new_txt))
    for m in reversed(vis_blocks):
        vm = None
        for line in m.group(0).split('\n'):
            mm = re.match(r'if \((\w+) != null\) \1\.Visibility = Visibility\.(\w+);', line.strip())
            if mm and mm.group(2) == 'Visible':
                vm = mm; break
        if not vm: continue
        view = VAR2VIEW.get(vm.group(1))
        if not view: continue
        new_txt = new_txt[:m.start()] + f'ShowPage("{view}");' + new_txt[m.end():]
    total_vis += len(vis_blocks)
    # 2. FindName 块删除（ShowPage 替换后残留）
    fn_blocks = list(fn_re.finditer(new_txt))
    for m in reversed(fn_blocks):
        new_txt = new_txt[:m.start()] + new_txt[m.end():]
    total_fn += len(fn_blocks)
    if vis_blocks or fn_blocks:
        io.open(fp, 'w', encoding='utf-8', newline='').write(new_txt)
        print(f'{fname}: vis={len(vis_blocks)} fn={len(fn_blocks)}')
    else:
        print(f'{fname}: 0')
print('TOTAL vis:', total_vis, 'fn:', total_fn)
