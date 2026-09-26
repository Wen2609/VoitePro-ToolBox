# -*- coding: utf-8 -*-
"""恢复被 lazy_xaml 误删的 DownloadView 块到 PageHost 自闭合标签之后（主内容 Grid 内）"""
import io, sys, subprocess
sys.stdout.reconfigure(encoding='utf-8')
out = subprocess.run(['git', 'show', 'HEAD:VioletToolBox/MainWindow.xaml'],
                     cwd=r'D:\doubao space\VioletToolBox', capture_output=True, text=True, encoding='utf-8')
head = out.stdout
lines = head.split('\n')
block = '\n'.join(lines[5310:5640])

fp = r'D:\doubao space\VioletToolBox\VioletToolBox\MainWindow.xaml'
x = io.open(fp, 'r', encoding='utf-8').read()
if 'Name="DownloadView"' in x:
    print('ALREADY restored, skip')
    sys.exit(0)
i = x.find('<ContentControl x:Name="PageHost"')
if i == -1:
    print('FAIL: PageHost not found')
    sys.exit(1)
j = x.find('/>', i)
insert_at = j + 2
new_x = x[:insert_at] + '\n' + block + x[insert_at:]
io.open(fp, 'w', encoding='utf-8', newline='').write(new_x)
print('restored at', insert_at, 'new len:', len(new_x))
