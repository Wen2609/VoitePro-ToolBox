# -*- coding: utf-8 -*-
"""替换 Page_EdlFlashView 占位为完整 EDL 页 XAML"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

p = r'D:\doubao space\VioletToolBox\VioletToolBox\MainWindow.xaml'
c = open(p, encoding='utf-8').read()

start_marker = '<DataTemplate x:Key="Page_EdlFlashView">'
end_marker = '<DataTemplate x:Key="Page_ColorOSAssistantView">'
start = c.index(start_marker)
end = c.index(end_marker)

new_xaml = '''                <DataTemplate x:Key="Page_EdlFlashView">
                        <Grid
                        Name="EdlFlashView"
                        Visibility="Collapsed"
                        Background="#FFF8F8F8">
                        <ScrollViewer VerticalScrollBarVisibility="Auto" HorizontalScrollBarVisibility="Disabled">
                            <StackPanel Margin="24,20,24,18">
                                <!-- 标题 -->
                                <StackPanel Orientation="Horizontal" Margin="0,0,0,16">
                                    <Border Width="46" Height="46" CornerRadius="23" Background="#FFE0EFFF" VerticalAlignment="Center">
                                        <TextBlock Text="EDL" FontSize="18" FontWeight="Bold" Foreground="#FF0A84FF" HorizontalAlignment="Center" VerticalAlignment="Center"/>
                                    </Border>
                                    <StackPanel Margin="14,0,0,0" VerticalAlignment="Center">
                                        <TextBlock Style="{StaticResource PageTitle}" Text="EDL 刷写" FontSize="22"/>
                                        <StackPanel Orientation="Horizontal" Margin="0,5,0,0">
                                            <TextBlock Text="9008 端口：" FontSize="12" Foreground="#FF8E8E93" VerticalAlignment="Center"/>
                                            <TextBlock x:Name="EdlPortStatusText" Text="未检测到" FontSize="12" Foreground="#FFD63333" VerticalAlignment="Center" FontWeight="SemiBold"/>
                                        </StackPanel>
                                    </StackPanel>
                                </StackPanel>

                                <Grid>
                                    <Grid.ColumnDefinitions>
                                        <ColumnDefinition Width="3*"/>
                                        <ColumnDefinition Width="14"/>
                                        <ColumnDefinition Width="2*"/>
                                    </Grid.ColumnDefinitions>

                                    <!-- 左列 -->
                                    <StackPanel Grid.Column="0">
                                        <!-- Firehose 模式 -->
                                        <Border Style="{StaticResource PageCard}" Margin="0,0,0,14">
                                            <StackPanel>
                                                <StackPanel Orientation="Horizontal" Margin="0,0,0,12"><svg:SvgViewbox Source="images/gaotongxiaolong.svg" Width="16" Height="16" Margin="0,1,8,0" VerticalAlignment="Center"/><TextBlock Style="{StaticResource PageTitle}" Text="Firehose 模式"/></StackPanel>
                                                <TextBlock Text="设备编程器 (devprg*.mbn)" FontSize="12" Foreground="#FF8E8E93"/>
                                                <Grid Margin="0,6,0,0">
                                                    <Grid.ColumnDefinitions><ColumnDefinition Width="*"/><ColumnDefinition Width="8"/><ColumnDefinition Width="68"/></Grid.ColumnDefinitions>
                                                    <TextBox x:Name="EdlDevPrgTextBox" Grid.Column="0" Height="34" Style="{StaticResource PageTextBox}" VerticalContentAlignment="Center"/>
                                                    <Button x:Name="EdlDevPrgBrowse" Grid.Column="2" Content="浏览" Style="{StaticResource PageSecondaryButton}" Height="34" Click="EdlDevPrgBrowse_Click"/>
                                                </Grid>
                                                <TextBlock Text="摘要文件 (*.bin)" FontSize="12" Foreground="#FF8E8E93" Margin="0,12,0,0"/>
                                                <Grid Margin="0,6,0,0">
                                                    <Grid.ColumnDefinitions><ColumnDefinition Width="*"/><ColumnDefinition Width="8"/><ColumnDefinition Width="68"/></Grid.ColumnDefinitions>
                                                    <TextBox x:Name="EdlDigestTextBox" Grid.Column="0" Height="34" Style="{StaticResource PageTextBox}" VerticalContentAlignment="Center"/>
                                                    <Button x:Name="EdlDigestBrowse" Grid.Column="2" Content="浏览" Style="{StaticResource PageSecondaryButton}" Height="34" Click="EdlDigestBrowse_Click"/>
                                                </Grid>
                                                <TextBlock Text="签名文件 (*.bin)" FontSize="12" Foreground="#FF8E8E93" Margin="0,12,0,0"/>
                                                <Grid Margin="0,6,0,0">
                                                    <Grid.ColumnDefinitions><ColumnDefinition Width="*"/><ColumnDefinition Width="8"/><ColumnDefinition Width="68"/></Grid.ColumnDefinitions>
                                                    <TextBox x:Name="EdlSigTextBox" Grid.Column="0" Height="34" Style="{StaticResource PageTextBox}" VerticalContentAlignment="Center"/>
                                                    <Button x:Name="EdlSigBrowse" Grid.Column="2" Content="浏览" Style="{StaticResource PageSecondaryButton}" Height="34" Click="EdlSigBrowse_Click"/>
                                                </Grid>
                                                <Button x:Name="EdlEnterFirehoseButton" Content="进入 Firehose" Style="{StaticResource PagePrimaryButton}" Height="38" Margin="0,14,0,0" Click="EdlEnterFirehose_Click"/>
                                            </StackPanel>
                                        </Border>

                                        <!-- ROM 包 -->
                                        <Border Style="{StaticResource PageCard}" Margin="0,0,0,14">
                                            <StackPanel>
                                                <StackPanel Orientation="Horizontal" Margin="0,0,0,12"><svg:SvgViewbox Source="images/yasuobao.svg" Width="16" Height="16" Margin="0,1,8,0" VerticalAlignment="Center"/><TextBlock Style="{StaticResource PageTitle}" Text="ROM 包"/></StackPanel>
                                                <TextBlock Text="选择解压后的 ROM 文件夹，或 OFP/OPS 加密包" FontSize="12" Foreground="#FF8E8E93"/>
                                                <Grid Margin="0,6,0,0">
                                                    <Grid.ColumnDefinitions><ColumnDefinition Width="*"/><ColumnDefinition Width="8"/><ColumnDefinition Width="68"/></Grid.ColumnDefinitions>
                                                    <TextBox x:Name="EdlRomPathTextBox" Grid.Column="0" Height="34" Style="{StaticResource PageTextBox}" VerticalContentAlignment="Center" IsReadOnly="True"/>
                                                    <Button x:Name="EdlRomBrowse" Grid.Column="2" Content="选择" Style="{StaticResource PageSecondaryButton}" Height="34" Click="EdlRomBrowse_Click"/>
                                                </Grid>
                                                <TextBlock Text="rawprogram XML 文件：" FontSize="12" Foreground="#FF8E8E93" Margin="0,12,0,0"/>
                                                <ListBox x:Name="EdlXmlList" Height="92" Margin="0,6,0,0" Background="#FFFBFCFE" BorderBrush="#FFE8E8E8" BorderThickness="1" ScrollViewer.VerticalScrollBarVisibility="Auto"/>
                                                <Grid Margin="0,8,0,0">
                                                    <Grid.ColumnDefinitions><ColumnDefinition Width="*"/><ColumnDefinition Width="8"/><ColumnDefinition Width="*"/><ColumnDefinition Width="8"/><ColumnDefinition Width="*"/></Grid.ColumnDefinitions>
                                                    <Button x:Name="EdlLoadButton" Grid.Column="0" Content="加载" Style="{StaticResource PagePrimaryButton}" Height="34" Click="EdlLoad_Click"/>
                                                    <Button x:Name="EdlXmlAllButton" Grid.Column="2" Content="全选" Style="{StaticResource PageSecondaryButton}" Height="34" Click="EdlXmlAll_Click"/>
                                                    <Button x:Name="EdlXmlNoneButton" Grid.Column="4" Content="反选" Style="{StaticResource PageSecondaryButton}" Height="34" Click="EdlXmlNone_Click"/>
                                                </Grid>
                                                <TextBlock x:Name="EdlRomInfoText" FontSize="12" Foreground="#FF8E8E93" Margin="0,10,0,0" TextWrapping="Wrap"/>
                                            </StackPanel>
                                        </Border>

                                        <!-- 选项 -->
                                        <Border Style="{StaticResource PageCard}">
                                            <StackPanel>
                                                <StackPanel Orientation="Horizontal" Margin="0,0,0,10"><svg:SvgViewbox Source="images/anquanyinsi.svg" Width="16" Height="16" Margin="0,1,8,0" VerticalAlignment="Center"/><TextBlock Style="{StaticResource PageTitle}" Text="选项"/></StackPanel>
                                                <CheckBox x:Name="EdlExportXmlCheckBox" Content="导出 XML（备份时生成 rawprogram XML）" Style="{StaticResource PageCheckBox}"/>
                                                <CheckBox x:Name="EdlProtectLun5CheckBox" Content="保护 LUN5（跳过 rawprogram5.xml）" Style="{StaticResource PageCheckBox}" Margin="0,8,0,0"/>
                                                <CheckBox x:Name="EdlSkipPatchCheckBox" Content="跳过 Patch XML" Style="{StaticResource PageCheckBox}" Margin="0,8,0,0"/>
                                                <CheckBox x:Name="EdlAutoRebootCheckBox" Content="刷写完成后自动重启" Style="{StaticResource PageCheckBox}" Margin="0,8,0,0"/>
                                            </StackPanel>
                                        </Border>
                                    </StackPanel>

                                    <!-- 右列 -->
                                    <StackPanel Grid.Column="2">
                                        <!-- 分区列表 -->
                                        <Border Style="{StaticResource PageCard}" Margin="0,0,0,14">
                                            <StackPanel>
                                                <StackPanel Orientation="Horizontal" Margin="0,0,0,10"><svg:SvgViewbox Source="images/shuaxin.svg" Width="16" Height="16" Margin="0,1,8,0" VerticalAlignment="Center"/><TextBlock Style="{StaticResource PageTitle}" Text="分区列表"/></StackPanel>
                                                <Grid>
                                                    <Grid.ColumnDefinitions><ColumnDefinition Width="*"/><ColumnDefinition Width="8"/><ColumnDefinition Width="96"/></Grid.ColumnDefinitions>
                                                    <TextBox x:Name="EdlSearchBox" Grid.Column="0" Height="32" Style="{StaticResource PageTextBox}" TextChanged="EdlSearch_TextChanged" VerticalContentAlignment="Center"/>
                                                    <TextBlock Grid.Column="2" Text="双击行选文件" FontSize="11" Foreground="#FF8E8E93" VerticalAlignment="Center" TextAlignment="Center"/>
                                                </Grid>
                                                <DataGrid x:Name="EdlPartitionGrid"
                                                          Height="300"
                                                          Margin="0,10,0,0"
                                                          AutoGenerateColumns="False"
                                                          IsReadOnly="True"
                                                          HeadersVisibility="Column"
                                                          GridLinesVisibility="Horizontal"
                                                          ColumnHeaderStyle="{StaticResource OugaFlashDataGridHeaderStyle}"
                                                          RowStyle="{StaticResource OugaFlashDataGridRowStyle}"
                                                          CellStyle="{StaticResource OugaFlashDataGridCellStyle}"
                                                          Background="#FFFFFFFF"
                                                          AlternatingRowBackground="#FFFAFBFD"
                                                          BorderBrush="#FFE8E8E8"
                                                          BorderThickness="1"
                                                          MouseDoubleClick="EdlPartitionGrid_MouseDoubleClick"
                                                          SelectionChanged="EdlPartitionGrid_SelectionChanged">
                                                    <DataGrid.Columns>
                                                        <DataGridTemplateColumn Header="✓" Width="36">
                                                            <DataGridTemplateColumn.CellTemplate>
                                                                <DataTemplate>
                                                                    <CheckBox IsChecked="{Binding IsSelected, Mode=TwoWay, UpdateSourceTrigger=PropertyChanged}" HorizontalAlignment="Center" VerticalAlignment="Center"/>
                                                                </DataTemplate>
                                                            </DataGridTemplateColumn.CellTemplate>
                                                        </DataGridTemplateColumn>
                                                        <DataGridTextColumn Header="分区" Binding="{Binding Name}" Width="*"/>
                                                        <DataGridTextColumn Header="LUN" Binding="{Binding Lun}" Width="52"/>
                                                        <DataGridTextColumn Header="起始" Binding="{Binding FirstLBA}" Width="86"/>
                                                        <DataGridTextColumn Header="大小" Binding="{Binding SizeFormatted}" Width="86"/>
                                                        <DataGridTextColumn Header="文件" Binding="{Binding FilePath}" Width="2*"/>
                                                    </DataGrid.Columns>
                                                </DataGrid>
                                            </StackPanel>
                                        </Border>

                                        <!-- 操作 -->
                                        <Border Style="{StaticResource PageCard}">
                                            <StackPanel>
                                                <StackPanel Orientation="Horizontal" Margin="0,0,0,10"><svg:SvgViewbox Source="images/shandian.svg" Width="16" Height="16" Margin="0,1,8,0" VerticalAlignment="Center"/><TextBlock Style="{StaticResource PageTitle}" Text="操作"/></StackPanel>
                                                <Grid>
                                                    <Grid.ColumnDefinitions><ColumnDefinition Width="*"/><ColumnDefinition Width="8"/><ColumnDefinition Width="*"/><ColumnDefinition Width="8"/><ColumnDefinition Width="*"/></Grid.ColumnDefinitions>
                                                    <Button x:Name="EdlReadPartitionsButton" Grid.Column="0" Content="读分区表" Style="{StaticResource PageSecondaryButton}" Height="36" Click="EdlReadPartitions_Click"/>
                                                    <Button x:Name="EdlReadSelectedButton" Grid.Column="2" Content="备份选定" Style="{StaticResource PageSecondaryButton}" Height="36" Click="EdlReadSelected_Click"/>
                                                    <Button x:Name="EdlEraseSelectedButton" Grid.Column="4" Content="擦除选定" Style="{StaticResource PageSecondaryButton}" Height="36" Click="EdlEraseSelected_Click"/>
                                                </Grid>
                                                <Grid Margin="0,8,0,0">
                                                    <Grid.ColumnDefinitions><ColumnDefinition Width="*"/><ColumnDefinition Width="8"/><ColumnDefinition Width="*"/></Grid.ColumnDefinitions>
                                                    <Button x:Name="EdlWriteSelectedButton" Grid.Column="0" Content="写入选定" Style="{StaticResource PageSecondaryButton}" Height="36" Click="EdlWriteSelected_Click"/>
                                                    <Button x:Name="EdlStopButton" Grid.Column="2" Content="停止操作" Style="{StaticResource PageSecondaryButton}" Height="36" IsEnabled="False" Click="EdlStop_Click"/>
                                                </Grid>
                                                <Button x:Name="EdlStartFlashButton" Content="开始刷入" Style="{StaticResource PagePrimaryButton}" Height="40" Margin="0,10,0,0" Click="EdlStartFlash_Click"/>
                                            </StackPanel>
                                        </Border>
                                    </StackPanel>
                                </Grid>

                                <!-- 日志 -->
                                <Border Style="{StaticResource PageCard}" Margin="0,14,0,0">
                                    <StackPanel>
                                        <StackPanel Orientation="Horizontal" Margin="0,0,0,8">
                                            <TextBlock Style="{StaticResource PageTitle}" Text="日志"/>
                                            <Button x:Name="EdlClearLogButton" Content="清空" Style="{StaticResource PageSecondaryButton}" Height="28" Margin="14,0,0,0" Click="EdlClearLog_Click"/>
                                        </StackPanel>
                                        <TextBox x:Name="EdlLogTextBox" Height="130" IsReadOnly="True" TextWrapping="Wrap" VerticalScrollBarVisibility="Auto" FontFamily="Consolas" FontSize="12" Background="#FFFBFCFE" BorderBrush="#FFE8E8E8" BorderThickness="1" Padding="8"/>
                                    </StackPanel>
                                </Border>

                                <!-- 进度 -->
                                <StackPanel Margin="0,14,0,0">
                                    <ProgressBar x:Name="EdlProgressBar" Height="6" Maximum="100" Value="0" Style="{StaticResource PageProgress}"/>
                                </StackPanel>
                            </StackPanel>
                        </ScrollViewer>
                        </Grid>
                    </DataTemplate>
'''

c = c[:start] + new_xaml + c[end:]
open(p, 'w', encoding='utf-8').write(c)
print('XAML replaced, new length:', len(c))
print('EdlPartitionGrid:', c.count('x:Name="EdlPartitionGrid"'))
print('EdlLogTextBox:', c.count('x:Name="EdlLogTextBox"'))
print('EdlStartFlashButton:', c.count('x:Name="EdlStartFlashButton"'))
