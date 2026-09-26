# -*- coding: utf-8 -*-
import io, sys
sys.stdout.reconfigure(encoding='utf-8')
files = [
    r'D:\doubao space\VioletToolBox\VioletToolBox\Themes\PageStyles.xaml',
    r'D:\doubao space\VioletToolBox\VioletToolBox\Themes\Controls.xaml',
    r'D:\doubao space\VioletToolBox\VioletToolBox\Themes\Colors.xaml',
]
keys = ['PagePrimaryButton', 'PageLabel', 'PageCheckBox', 'PageTitle', 'PageCard', 'PageSecondaryButton', 'BoolToVisibilityConverter']
out = []
for f in files:
    try:
        x = io.open(f, 'r', encoding='utf-8').read()
        out.append('%s len=%d' % (f.split('\\')[-1], len(x)))
        for key in keys:
            c = x.count('x:Key="%s"' % key)
            if c:
                # 提取定义开头
                i = x.find('x:Key="%s"' % key)
                seg = x[max(0, i-200):i+400]
                out.append('  %s=%d ctx:%s' % (key, c, seg.replace('\n', ' ')[:260]))
    except Exception as ex:
        out.append('%s ERR %s' % (f, ex))
io.open(r'D:\doubao space\VioletToolBox\themes_check.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('done')
