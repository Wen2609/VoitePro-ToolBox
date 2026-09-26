# -*- coding: utf-8 -*-
import io, re, sys
sys.stdout.reconfigure(encoding='utf-8')
c = io.open(r'D:\doubao space\VioletToolBox\VioletToolBox\MainWindow.xaml', 'r', encoding='utf-8').read()
tpl = c.split('懒加载页面模板', 1)[1].split('</FrameworkElement.Resources>', 1)[0]
names = set(re.findall(r'(?:x:Name|Name)\s*=\s*"([^"]+)"', tpl))
for n in ['EdlFlashPackTextBox', 'EdlLoaderTextBox', 'EdlPortComboBox', 'photoGallery']:
    print(n, 'in names:', n in names)
print('total:', len(names))
print('tpl len:', len(tpl))
