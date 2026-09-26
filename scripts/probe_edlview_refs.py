# -*- coding: utf-8 -*-
import io, sys, re
sys.stdout.reconfigure(encoding='utf-8')
base = r'D:\doubao space\VioletToolBox\VioletToolBox'
for f in ['MainWindow.BackupAssistant.cs', 'MainWindow.ColorOSAssistant.cs', 'MainWindow.HiddenEnvironment.cs', 'MainWindow.Payload.cs']:
    c = io.open(base + '\\' + f, 'r', encoding='utf-8').read()
    for m in re.finditer(r'.{180}FindControlInPages\("EdlFlashView"\).{180}', c, re.S):
        print('=== ' + f + ' ===')
        print(m.group(0).replace('\n', ' ')[:400])
        print()
