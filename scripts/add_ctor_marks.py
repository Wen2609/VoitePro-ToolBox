# -*- coding: utf-8 -*-
import io, sys
sys.stdout.reconfigure(encoding='utf-8')
fp = r'D:\doubao space\VioletToolBox\VioletToolBox\MainWindow.xaml.cs'
t = io.open(fp, 'r', encoding='utf-8').read()
marks = [
    ('            allPartitions.CollectionChanged += AllPartitions_CollectionChanged;',
     '            try { System.IO.File.AppendAllText(System.IO.Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "startup.log"), "m1 before cc\\r\\n"); } catch { }\n            allPartitions.CollectionChanged += AllPartitions_CollectionChanged;'),
    ('            UpdatePartitionSelectionSummary();',
     '            try { System.IO.File.AppendAllText(System.IO.Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "startup.log"), "m2 before upss\\r\\n"); } catch { }\n            UpdatePartitionSelectionSummary();'),
    ('            InitializeAutoRootModeUiState();',
     '            try { System.IO.File.AppendAllText(System.IO.Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "startup.log"), "m3 before armus\\r\\n"); } catch { }\n            InitializeAutoRootModeUiState();'),
    ('            UpdateAvbModeFileInputs();',
     '            try { System.IO.File.AppendAllText(System.IO.Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "startup.log"), "m4 before amfi\\r\\n"); } catch { }\n            UpdateAvbModeFileInputs();'),
    ('            InitializeVioletDownload();',
     '            try { System.IO.File.AppendAllText(System.IO.Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "startup.log"), "m5 before ivd\\r\\n"); } catch { }\n            InitializeVioletDownload();'),
    ('            InitializeDeviceStatusMonitoring();',
     '            try { System.IO.File.AppendAllText(System.IO.Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "startup.log"), "m6 before idsm\\r\\n"); } catch { }\n            InitializeDeviceStatusMonitoring();'),
    ('            InitializeLanguageUi();',
     '            try { System.IO.File.AppendAllText(System.IO.Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "startup.log"), "m7 before ilu\\r\\n"); } catch { }\n            InitializeLanguageUi();'),
]
for old, new in marks:
    if old in t:
        t = t.replace(old, new, 1)
        print('marked:', old.strip()[:60])
    else:
        print('NOT FOUND:', old.strip()[:60])
io.open(fp, 'w', encoding='utf-8', newline='').write(t)
print('done')
