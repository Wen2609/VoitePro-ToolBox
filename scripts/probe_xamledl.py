# -*- coding: utf-8 -*-
import io, sys, re
sys.stdout.reconfigure(encoding='utf-8')
base = r'D:\doubao space\VioletToolBox\VioletToolBox'
cs = io.open(base + r'\MainWindow.xaml.cs', 'r', encoding='utf-8').read()
for pat in ['StartEdlCloudLoaderRefresh', 'IsEdlBasebandFingerprintBackupPartitionLabel', 'IsEdlDataPartitionLabel', 'StripEdlSlotSuffix']:
    for m in re.finditer(r'.{140}' + pat + r'.{140}', cs):
        print('=== ' + pat + ' ===')
        print(m.group(0).replace('\n', ' ')[:320])
        print()
