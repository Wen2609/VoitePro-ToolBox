# -*- coding: utf-8 -*-
import re
c = open(r'D:\doubao space\VioletToolBox\VioletToolBox\Themes\Controls.xaml', encoding='utf-8').read()
out = []
for key in ['PrimaryButton', 'HeroCard', 'WhiteButton', 'ActionCardButton', 'GhostButton', 'SecondaryButton', 'ToggleSwitch', 'StatusBadge', 'SectionTitle', 'CardTitle']:
    m = re.search(r'<Style x:Key="' + key + r'".*?</Style>', c, re.S)
    if m:
        block = m.group(0)
        setters = re.findall(r'<Setter Property="(\w+)" Value="([^"]*)"', block)
        out.append('### ' + key)
        for p, v in setters[:8]:
            out.append('  %s=%s' % (p, v))
        # 触发器中颜色
        trig = re.findall(r'<Setter[^>]*Property="Background"[^>]*Value="([^"]*)"', block)
        if trig:
            out.append('  trigger-bg: ' + ', '.join(trig[:4]))
        # Background 直接值
        bg = re.findall(r'Background="([^"]+)"', block)
        if bg:
            out.append('  bg-values: ' + ', '.join(bg[:4]))
        out.append('')
open(r'D:\doubao space\VioletToolBox\controls_dump.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('done')
