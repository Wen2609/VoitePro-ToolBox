# -*- coding: utf-8 -*-
"""EDL DataTemplate 自包含 DataGrid 样式，消除对局部资源 OugaFlash* 的依赖"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
p = r'D:\doubao space\VioletToolBox\VioletToolBox\MainWindow.xaml'
c = open(p, encoding='utf-8').read()

# 1. 在 EdlFlashView Grid 后插入 Grid.Resources
old_grid = '''                        Name="EdlFlashView"
                        Visibility="Collapsed"
                        Background="#FFF8F8F8">'''
new_grid = '''                        Name="EdlFlashView"
                        Visibility="Collapsed"
                        Background="#FFF8F8F8">
                        <Grid.Resources>
                                <Style x:Key="EdlDgHeaderStyle" TargetType="{x:Type DataGridColumnHeader}">
                                    <Setter Property="Height" Value="32"/>
                                    <Setter Property="Background" Value="#FFF4F4F4"/>
                                    <Setter Property="Foreground" Value="#FF1D1D1F"/>
                                    <Setter Property="FontWeight" Value="SemiBold"/>
                                    <Setter Property="BorderThickness" Value="0,0,0,1"/>
                                    <Setter Property="BorderBrush" Value="#FFE9E9E9"/>
                                    <Setter Property="HorizontalContentAlignment" Value="Center"/>
                                </Style>
                                <Style x:Key="EdlDgRowStyle" TargetType="{x:Type DataGridRow}">
                                    <Setter Property="Background" Value="#FFFFFFFF"/>
                                    <Style.Triggers>
                                        <Trigger Property="AlternationIndex" Value="1">
                                            <Setter Property="Background" Value="#FFFCFBFD"/>
                                        </Trigger>
                                        <Trigger Property="IsMouseOver" Value="True">
                                            <Setter Property="Background" Value="#FFF5F5F5"/>
                                        </Trigger>
                                    </Style.Triggers>
                                </Style>
                                <Style x:Key="EdlDgCellStyle" TargetType="{x:Type DataGridCell}">
                                    <Setter Property="BorderThickness" Value="0"/>
                                    <Setter Property="VerticalContentAlignment" Value="Center"/>
                                    <Setter Property="Padding" Value="6,0"/>
                                    <Setter Property="FontSize" Value="12"/>
                                    <Setter Property="Foreground" Value="#FF1D1D1F"/>
                                </Style>
                            </Grid.Resources>'''
assert c.count(old_grid) == 1, 'grid header anchor not found'
c = c.replace(old_grid, new_grid)

# 2. 替换 3 个样式引用
c = c.replace('ColumnHeaderStyle="{StaticResource OugaFlashDataGridHeaderStyle}"',
              'ColumnHeaderStyle="{StaticResource EdlDgHeaderStyle}"')
c = c.replace('RowStyle="{StaticResource OugaFlashDataGridRowStyle}"',
              'RowStyle="{StaticResource EdlDgRowStyle}"')
c = c.replace('CellStyle="{StaticResource OugaFlashDataGridCellStyle}"',
              'CellStyle="{StaticResource EdlDgCellStyle}"')

open(p, 'w', encoding='utf-8').write(c)
print('patched. EdlDgHeaderStyle:', c.count('EdlDgHeaderStyle'))
print('OugaFlashDataGrid in EDL remains:', c.count('OugaFlashDataGridHeaderStyle'))
