# -*- coding: utf-8 -*-
import io, re, sys
sys.stdout.reconfigure(encoding='utf-8')
fp = r'D:\doubao space\VioletToolBox\VioletToolBox\MainWindow.xaml'
# 1) 恢复原始（未禁用、未空化）版
bak = io.open(fp + '.bak', 'r', encoding='utf-8').read()
x = bak
print('restored from .bak, x:Key Page_ count:', x.count('x:Key="Page_'))
# 2) 修复 Resources 结构：删除 </ResourceDictionary>（原 L412，ResourceDictionary 内容后的第一个闭）
# 定位：<ResourceDictionary>（L24）后第一个 </ResourceDictionary>
rd_open = x.find('<ResourceDictionary>', x.find('<FrameworkElement.Resources>'))
rd_close = x.find('</ResourceDictionary>', rd_open)
fe_close = x.find('</FrameworkElement.Resources>', rd_open)
print('rd_open L', x[:rd_open].count('\n') + 1, 'rd_close L', x[:rd_close].count('\n') + 1, 'fe_close L', x[:fe_close].count('\n') + 1)
# 删除 rd_close 处的 </ResourceDictionary>
x2 = x[:rd_close] + x[rd_close + len('</ResourceDictionary>'):]
# 3) 在 </FrameworkElement.Resources> 前插入 </ResourceDictionary>
fe2 = x2.find('</FrameworkElement.Resources>')
x3 = x2[:fe2] + '</ResourceDictionary>\n' + x2[fe2:]
io.open(fp, 'w', encoding='utf-8', newline='').write(x3)
print('Resources structure FIXED: dictionary now wraps Style+16 templates')
print('rd open/close balance:', x3.count('<ResourceDictionary>'), x3.count('</ResourceDictionary>'))
