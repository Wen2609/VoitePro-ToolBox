# -*- coding: utf-8 -*-
import io, re, sys
sys.stdout.reconfigure(encoding='utf-8')
fp = r'D:\doubao space\VioletToolBox\VioletToolBox\MainWindow.xaml'
x = io.open(fp, 'r', encoding='utf-8').read()
# 定位 Page_AutorootView 模板完整区间
tpls = [(m2.group(1), m2.start()) for m2 in re.finditer(r'<DataTemplate\s+x:Key="(?:DISABLED_)?(Page_[A-Za-z0-9]+)"', x)]
for i, (key, pos) in enumerate(tpls):
    if key == 'Page_AutorootView':
        end = tpls[i+1][1] if i+1 < len(tpls) else len(x)
        # 找 </DataTemplate> 结束（从 pos 开始，不跨过下一个模板）
        seg = x[pos:end]
        close = seg.rfind('</DataTemplate>')
        if close == -1:
            print('ERROR: no closing DataTemplate')
            sys.exit(1)
        full_end = pos + close + len('</DataTemplate>')
        # 备份
        orig = x[pos:full_end]
        io.open(r'D:\doubao space\VioletToolBox\autoroot_tpl_backup.xaml', 'w', encoding='utf-8').write(orig)
        print('backup len=', len(orig))
        # 空模板替换
        empty = '<DataTemplate x:Key="Page_AutorootView"><Grid Name="AutorootView" Visibility="Collapsed" Background="#FFFAFAFA" Width="960"><TextBlock Text="AUTOROOT" FontSize="20" HorizontalAlignment="Center" VerticalAlignment="Center"/></Grid></DataTemplate>'
        x2 = x[:pos] + empty + x[full_end:]
        io.open(fp, 'w', encoding='utf-8', newline='').write(x2)
        print('AutorootView template replaced with minimal grid')
        break
