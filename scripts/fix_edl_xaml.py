# -*- coding: utf-8 -*-
import io, sys, re
sys.stdout.reconfigure(encoding='utf-8')
fp = r'D:\doubao space\VioletToolBox\VioletToolBox\MainWindow.xaml'
x = io.open(fp, 'r', encoding='utf-8').read()

# 1) 透明修复（正则）
x2 = re.sub(r'[ \t]*AllowsTransparency="True"\r?\n', '', x, count=1)
x2 = re.sub(r'[ \t]*Background="#00FFFFFF"', 'Background="#FFFAFAFC"', x2, count=1)
assert x2 != x, 'transparency anchors not found'

# 2) EDL 模板配对计数替换
i = x2.find('<DataTemplate x:Key="Page_EdlFlashView">')
assert i != -1, 'EdlFlashView template NOT FOUND'
depth = 0
j = i
while j < len(x2):
    # 找下一个 <DataTemplate 或 </DataTemplate>
    o = x2.find('<DataTemplate', j)
    c = x2.find('</DataTemplate>', j)
    if o == -1 and c == -1:
        break
    if o != -1 and (c == -1 or o < c):
        depth += 1
        j = o + len('<DataTemplate')
    else:
        depth -= 1
        j = c + len('</DataTemplate>')
        if depth == 0:
            break
assert depth == 0, 'template end not balanced'
placeholder = """<DataTemplate x:Key="Page_EdlFlashView">
                        <Grid
                        Name="EdlFlashView"
                        Visibility="Collapsed"
                        Background="#FFF8F8F8">
                        <StackPanel VerticalAlignment="Center" HorizontalAlignment="Center">
                            <Border Width="68" Height="68" CornerRadius="34" Background="#FFE0EFFF" HorizontalAlignment="Center">
                                <TextBlock Text="EDL" FontSize="20" FontWeight="Bold" Foreground="#FF0A84FF" HorizontalAlignment="Center" VerticalAlignment="Center"/>
                            </Border>
                            <TextBlock Text="EDL 刷写" FontSize="21" FontWeight="SemiBold" Foreground="#FF1D1D1F" HorizontalAlignment="Center" Margin="0,18,0,0"/>
                            <TextBlock Text="该模块已在精简版中移除，敬请期待后续版本" FontSize="13" Foreground="#FF8E8E93" HorizontalAlignment="Center" Margin="0,10,0,0"/>
                        </StackPanel>
                        </Grid>
                    </DataTemplate>"""
x2 = x2[:i] + placeholder + x2[j:]
io.open(fp, 'w', encoding='utf-8', newline='').write(x2)
print('transparency + EdlFlashView placeholder applied (removed', j-i, 'chars)')
