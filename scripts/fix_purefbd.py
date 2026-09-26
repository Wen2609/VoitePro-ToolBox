# -*- coding: utf-8 -*-
"""移动仅FBD到Bottom Row + Bottom按钮缩宽——按行号精确改"""
import io, sys
sys.stdout.reconfigure(encoding='utf-8')
p = r'D:\doubao space\VioletToolBox\VioletToolBox\MainWindow.xaml'
c = io.open(p, 'r', encoding='utf-8').read()
lines = c.split('\n')
print('total lines:', len(lines))

# 找关键行号
def find_line(pat, start=0):
    for i in range(start, len(lines)):
        if pat in lines[i]:
            return i
    return -1

# 1. Top Row 的 仅FBD CheckBox 行
i_purefbd_top = find_line('PureFBDCheckBox" Content="仅FBD"')
print('PureFBD top at L', i_purefbd_top+1)
# 2. Bottom Row StackPanel 开标签
i_bottom_sp = find_line('<StackPanel Grid.Row="2" Orientation="Horizontal">')
print('Bottom StackPanel at L', i_bottom_sp+1)

if i_purefbd_top < 0 or i_bottom_sp < 0:
    print('ANCHOR NOT FOUND')
    sys.exit(1)

# 提取 Top 仅FBD 行（删除）
purefbd_line = lines[i_purefbd_top]
# 从 Top 删除（如果它在 Top Row 区域，即 i_bottom_sp 之前）
if i_purefbd_top < i_bottom_sp:
    del lines[i_purefbd_top]
    # 行号偏移：bottom_sp 减 1
    i_bottom_sp -= 1
    print('removed PureFBD from Top Row')

# 在 Bottom Row StackPanel 后插入仅FBD（在 ARB 按钮前）
new_check = '                                            <CheckBox x:Name="PureFBDCheckBox" Content="仅FBD" Style="{StaticResource PageCheckBox}" Checked="PureFBDCheckBox_Checked" ToolTip="没有Fastboot的机型勾选这个，天玑处理器设备请勿勾选" Margin="0,0,8,0" VerticalAlignment="Center"/>'
lines.insert(i_bottom_sp+1, new_check)
print('inserted PureFBD at Bottom Row, new L', i_bottom_sp+2)

# 3. Bottom Row 三个按钮 Width 153 -> 120（在 Bottom Row 区域内，直到 </StackPanel>）
# 找 Bottom Row 结束
i_end = i_bottom_sp
while i_end < len(lines) and '</StackPanel>' not in lines[i_end]:
    i_end += 1
print('Bottom Row ends at L', i_end+1)
# 找区域内的 Width="153" 并改 120
cnt = 0
for i in range(i_bottom_sp, min(i_end+1, len(lines))):
    if 'Width="153"' in lines[i]:
        lines[i] = lines[i].replace('Width="153"', 'Width="120"')
        cnt += 1
print('width 153->120 changed:', cnt)

io.open(p, 'w', encoding='utf-8', newline='').write('\n'.join(lines))
print('written OK')
