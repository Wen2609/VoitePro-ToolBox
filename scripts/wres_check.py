# -*- coding: utf-8 -*-
import io, re, sys
sys.stdout.reconfigure(encoding='utf-8')
x = io.open(r'D:\doubao space\VioletToolBox\VioletToolBox\MainWindow.xaml', 'r', encoding='utf-8').read()
# 找 Window.Resources 定义区（第一个 ResourceDictionary 到 Page_ScreenMirrorView 前）
wstart = x.find('<FrameworkElement.Resources>')
wpos = x.find('<DataTemplate', wstart)
wres = x[wstart:wpos]
out = []
for key in ['PagePrimaryButton', 'PageLabel', 'PageCheckBox', 'PageTitle', 'PageCard', 'PageSecondaryButton', 'BoolToVisibilityConverter']:
    m = re.search(r'<Style[^>]*x:Key="%s"[^>]*>' % key, wres)
    if m:
        # 找该 style 结束（</Style>）
        e = wres.find('</Style>', m.start())
        seg = wres[m.start():e]
        # 特征
        has_tpl = '<Setter Property="Template">' in seg or 'ControlTemplate' in seg
        basedon = re.search(r'BasedOn="\{StaticResource ([^}]+)\}"', seg)
        tgt = re.search(r'TargetType="([^"]+)"', seg)
        refs = re.findall(r'\{StaticResource ([^}]+)\}', seg)
        out.append('%s: tpl=%s basedon=%s target=%s refs=%s len=%d' % (key, has_tpl, basedon.group(1) if basedon else None, tgt.group(1) if tgt else None, refs[:6], len(seg)))
    else:
        out.append(key + ': NOT IN Window.Resources')
io.open(r'D:\doubao space\VioletToolBox\wres_check.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('done')
