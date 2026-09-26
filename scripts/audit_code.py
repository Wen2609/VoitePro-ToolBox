# -*- coding: utf-8 -*-
"""项目代码审计：统计问题模式"""
import io, re, os, sys, glob
sys.stdout.reconfigure(encoding='utf-8')
root = r'D:\doubao space\VioletToolBox\VioletToolBox'
alltext = ''
files = []
for f in glob.glob(os.path.join(root, '*.cs')):
    try:
        t = io.open(f, 'r', encoding='utf-8', errors='ignore').read()
        alltext += '\n' + t
        files.append((os.path.basename(f), len(t.splitlines())))
    except Exception as e:
        print('ERR', f, e)

print('=== cs files (top by lines) ===')
for n, l in sorted(files, key=lambda x: -x[1])[:12]:
    print(f'  {l:>7}  {n}')

print('\n=== problem patterns ===')
def cnt(pat):
    return len(re.findall(pat, alltext))
print('empty catch{}:      ', cnt(r'catch\s*(\([^)]*\))?\s*\{\s*\}'))
print('Thread.Sleep:      ', cnt(r'Thread\.Sleep'))
print('async void:        ', cnt(r'async\s+void'))
print('Task.Run:          ', cnt(r'Task\.Run'))
print('MessageBox.Show:   ', cnt(r'MessageBox\.Show'))
print('TODO/FIXME:        ', cnt(r'TODO|FIXME|HACK'))
print('Dispatcher.Invoke: ', cnt(r'Dispatcher\.Invoke'))
print('total lines:       ', len(alltext.splitlines()))

# 全局未捕获异常处理检查
print('\n=== global exception handlers ===')
print('DispatcherUnhandledException:', 'DispatcherUnhandledException' in alltext)
print('AppDomain.UnhandledException:', 'AppDomain' in alltext and 'UnhandledException' in alltext)
print('TaskScheduler.UnobservedTaskException:', 'UnobservedTaskException' in alltext)

# 设置持久化检查
print('\n=== settings persistence ===')
print('Properties.Settings:', 'Properties.Settings' in alltext or 'Settings.Default' in alltext)
print('Registry:', 'Registry' in alltext)
print('AppData file:', 'AppData' in alltext)

# 深色模式
print('\n=== dark mode / theme ===')
print('DarkMode/DarkTheme:', 'DarkMode' in alltext or 'DarkTheme' in alltext)

# 自动更新
print('\n=== auto update ===')
print('Update check:', 'Update' in alltext and ('GitHub' in alltext or 'release' in alltext.lower()))

# 日志
print('\n=== logging ===')
print('File.AppendAllText/StreamWriter:', 'AppendAllText' in alltext or 'StreamWriter' in alltext)
