# -*- coding: utf-8 -*-
import io, re, sys
sys.stdout.reconfigure(encoding='utf-8')
fp = r'D:\doubao space\VioletToolBox\VioletToolBox\MainWindow.xaml'
x = io.open(fp, 'r', encoding='utf-8').read()
# 扩展功能区 6 个按钮：Padding 8→5、图标 16→13、Margin 5→3、TextBlock 加 TextTrimming
i = x.find('x:Key="Page_BasicFlashView"')
j = x.find('</DataTemplate>', i)
seg = x[i:j]
k = seg.find('扩展功能')
seg2 = seg[k:]
cnt = 0
# 每个按钮内：Padding="8,0" -> "5,0"
seg2_new = re.sub(r'(<Button[^>]*?)Padding="8,0"', lambda m: m.group(1) + 'Padding="5,0"', seg2)
seg2_new = re.sub(r'(<svg:SvgViewbox Source="images/(?:geshihuasdka|guge|adb|miui|ddr|jidi)[^"]*" )Width="16" Height="16"( Margin="0,0,)5(,0)"/>',
                  lambda m: m.group(1) + 'Width="13" Height="13"' + m.group(2) + '3' + m.group(3) + '"/>', seg2_new)
seg2_new = re.sub(r'(<TextBlock Text="[^"]*" VerticalAlignment="Center")(/>)', lambda m: m.group(1) + ' TextTrimming="CharacterEllipsis"' + m.group(2), seg2_new)
x = x[:i] + seg[:k] + seg2_new + x[j:]
io.open(fp, 'w', encoding='utf-8', newline='').write(x)
print('extended-function buttons: padding 5, icon 13, trimming added')
