# -*- coding: utf-8 -*-
"""修复 MainWindow.EdlFlash.cs：命名空间 + alias + Dispatcher + 枚举"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
p = r'D:\doubao space\VioletToolBox\VioletToolBox\MainWindow.EdlFlash.cs'
c = open(p, encoding='utf-8').read()

# 1. 命名空间
c = c.replace('namespace VioletToolBox', 'namespace WpfApp1')

# 2. using alias（消除 WinForms 冲突）
old_using = 'using System.Windows;\nusing System.Windows.Controls;\n'
new_using = old_using + '''using TextBox = System.Windows.Controls.TextBox;
using ListBox = System.Windows.Controls.ListBox;
using CheckBox = System.Windows.Controls.CheckBox;
using ProgressBar = System.Windows.Controls.ProgressBar;
using OpenFileDialog = Microsoft.Win32.OpenFileDialog;
using MessageBox = System.Windows.MessageBox;
'''
c = c.replace(old_using, new_using, 1)

# 3. Dispatcher 实例化
c = c.replace('Dispatcher.BeginInvoke(new Action', 'this.Dispatcher.BeginInvoke(new Action')

# 4. 枚举值
c = c.replace('RomPackageKind.Official =>', 'RomPackageKind.OfficialSfp =>')
c = c.replace('RomPackageKind.ThirdParty => "第三方包",\n            RomPackageKind.Unlocked => "解锁包",', 'RomPackageKind.ThirdParty => "第三方包",')

open(p, 'w', encoding='utf-8').write(c)
print('patched')
print('namespace WpfApp1:', c.count('namespace WpfApp1'))
print('TextBox alias:', c.count('using TextBox ='))
print('this.Dispatcher:', c.count('this.Dispatcher.BeginInvoke'))
print('OfficialSfp:', c.count('OfficialSfp'))
print('Unlocked leftover:', c.count('Unlocked'))
