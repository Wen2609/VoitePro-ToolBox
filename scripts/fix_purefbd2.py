# -*- coding: utf-8 -*-
"""继续改 Bottom Row 剩余 Width 153 -> 120"""
import io, sys
sys.stdout.reconfigure(encoding='utf-8')
p = r'D:\doubao space\VioletToolBox\VioletToolBox\MainWindow.xaml'
c = io.open(p, 'r', encoding='utf-8').read()
lines = c.split('\n')

# Bottom Row 范围：StackPanel Grid.Row="2" 到其匹配的 </StackPanel>
# 精确：找 "<!-- Bottom Row -->" 到 Grid 结束 "</Grid>"（L3968 附近）
start = next(i for i, l in enumerate(lines) if '<!-- Bottom Row -->' in l)
# Bottom Row 的 </StackPanel> 是 start 后第二个（第一个是内部按钮的）
end = start + 1
stack_depth = 0
for i in range(start, len(lines)):
    if '<StackPanel' in lines[i]:
        stack_depth += 1
    if '</StackPanel>' in lines[i]:
        stack_depth -= 1
        if stack_depth == 0:
            end = i
            break
print('Bottom Row: L', start+1, 'to L', end+1)

cnt = 0
for i in range(start, end+1):
    if 'Width="153"' in lines[i]:
        lines[i] = lines[i].replace('Width="153"', 'Width="120"')
        cnt += 1
print('width 153->120 changed:', cnt)

io.open(p, 'w', encoding='utf-8', newline='').write('\n'.join(lines))
print('written OK')
