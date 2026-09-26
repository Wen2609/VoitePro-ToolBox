# -*- coding: utf-8 -*-
import io, sys
sys.stdout.reconfigure(encoding='utf-8')
fp = r'D:\doubao space\VioletToolBox\VioletToolBox\MainWindow.xaml'
x = io.open(fp, 'r', encoding='utf-8').read()
backup = io.open(r'D:\doubao space\VioletToolBox\autoroot_tpl_backup.xaml', 'r', encoding='utf-8').read()
old = '<DataTemplate x:Key="Page_AutorootView"><Grid Name="AutorootView" Visibility="Collapsed" Background="#FFFAFAFA" Width="960"><TextBlock Text="AUTOROOT" FontSize="20" HorizontalAlignment="Center" VerticalAlignment="Center"/></Grid></DataTemplate>'
if old in x:
    x = x.replace(old, backup, 1)
    io.open(fp, 'w', encoding='utf-8', newline='').write(x)
    print('AutorootView template restored, new len=', len(x))
else:
    print('empty template NOT FOUND - check state')
