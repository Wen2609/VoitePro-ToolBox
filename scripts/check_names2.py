# -*- coding: utf-8 -*-
import io, re, sys
sys.stdout.reconfigure(encoding='utf-8')
c = io.open(r'D:\doubao space\VioletToolBox\VioletToolBox\MainWindow.xaml', 'r', encoding='utf-8').read()
tpl_region = c.split('懒加载页面模板', 1)[1].split('</FrameworkElement.Resources>', 1)[0]
name2type = {}
for m in re.finditer(r'<(\w+:?[A-Za-z]+)\s+[^>]*?(?:x:Name|Name)="([^"]+)"', tpl_region):
    tag, name = m.group(1), m.group(2)
    if ':' in tag:
        prefix, cls = tag.split(':', 1)
    else:
        prefix, cls = '', tag
    name2type[name] = (prefix, cls)
print('EdlFlashPackTextBox in name2type:', 'EdlFlashPackTextBox' in name2type, name2type.get('EdlFlashPackTextBox'))
print('EdlLoaderTextBox:', 'EdlLoaderTextBox' in name2type, name2type.get('EdlLoaderTextBox'))
print('EdlPortComboBox:', 'EdlPortComboBox' in name2type, name2type.get('EdlPortComboBox'))
print('total:', len(name2type))
