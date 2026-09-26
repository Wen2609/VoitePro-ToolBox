# -*- coding: utf-8 -*-
import io, sys
sys.stdout.reconfigure(encoding='utf-8')
p = r'D:\doubao space\VioletToolBox\lazy_cs2.py'
t = io.open(p, 'r', encoding='utf-8').read()
old = "tpl_region = c.split('懒加载页面模板', 1)[1].split('</FrameworkElement.Resources>', 1)[0]"
new = "tpl_region = c  # 全文提取：懒加载模板区 + 主内容区（含恢复的 DownloadView 块）"
if old in t:
    t = t.replace(old, new, 1)
    print('tpl_region scope CHANGED to full XAML')
else:
    print('ANCHOR NOT FOUND')
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('saved')
