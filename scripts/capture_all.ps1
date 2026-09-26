powershell -ExecutionPolicy Bypass -File "D:\doubao space\VioletToolBox\scripts\ui_nav4.ps1" -Name "刷写功能" -Out "D:\doubao space\VioletToolBox\grp.png" 2>&1 | ForEach-Object { $_.ToString() } | Select-Object -Last 1
Start-Sleep 1
powershell -ExecutionPolicy Bypass -File "D:\doubao space\VioletToolBox\scripts\ui_nav4.ps1" -Name "基本刷入" -Out "D:\doubao space\VioletToolBox\p1_basic.png" 2>&1 | ForEach-Object { $_.ToString() } | Select-Object -Last 1
Start-Sleep 1
powershell -ExecutionPolicy Bypass -File "D:\doubao space\VioletToolBox\scripts\ui_nav4.ps1" -Name "可视刷写" -Out "D:\doubao space\VioletToolBox\p2_fastboot.png" 2>&1 | ForEach-Object { $_.ToString() } | Select-Object -Last 1
Start-Sleep 1
powershell -ExecutionPolicy Bypass -File "D:\doubao space\VioletToolBox\scripts\ui_nav4.ps1" -Name "欧加线刷" -Out "D:\doubao space\VioletToolBox\p3_oujia.png" 2>&1 | ForEach-Object { $_.ToString() } | Select-Object -Last 1
Start-Sleep 1
powershell -ExecutionPolicy Bypass -File "D:\doubao space\VioletToolBox\scripts\ui_nav4.ps1" -Name "EDL刷写" -Out "D:\doubao space\VioletToolBox\p14_edl.png" 2>&1 | ForEach-Object { $_.ToString() } | Select-Object -Last 1
Start-Sleep 1
powershell -ExecutionPolicy Bypass -File "D:\doubao space\VioletToolBox\scripts\ui_nav4.ps1" -Name "降级助手" -Out "D:\doubao space\VioletToolBox\p4_coloros.png" 2>&1 | ForEach-Object { $_.ToString() } | Select-Object -Last 1
Start-Sleep 1
powershell -ExecutionPolicy Bypass -File "D:\doubao space\VioletToolBox\scripts\ui_nav4.ps1" -Name "实用功能" -Out "D:\doubao space\VioletToolBox\grp.png" 2>&1 | ForEach-Object { $_.ToString() } | Select-Object -Last 1
Start-Sleep 1
powershell -ExecutionPolicy Bypass -File "D:\doubao space\VioletToolBox\scripts\ui_nav4.ps1" -Name "隐藏环境" -Out "D:\doubao space\VioletToolBox\p5_hidden.png" 2>&1 | ForEach-Object { $_.ToString() } | Select-Object -Last 1
Start-Sleep 1
powershell -ExecutionPolicy Bypass -File "D:\doubao space\VioletToolBox\scripts\ui_nav4.ps1" -Name "系统分区" -Out "D:\doubao space\VioletToolBox\p6_systemzone.png" 2>&1 | ForEach-Object { $_.ToString() } | Select-Object -Last 1
Start-Sleep 1
powershell -ExecutionPolicy Bypass -File "D:\doubao space\VioletToolBox\scripts\ui_nav4.ps1" -Name "自动root" -Out "D:\doubao space\VioletToolBox\p7_autoroot.png" 2>&1 | ForEach-Object { $_.ToString() } | Select-Object -Last 1
Start-Sleep 1
powershell -ExecutionPolicy Bypass -File "D:\doubao space\VioletToolBox\scripts\ui_nav4.ps1" -Name "应用管理" -Out "D:\doubao space\VioletToolBox\p8_appmgmt.png" 2>&1 | ForEach-Object { $_.ToString() } | Select-Object -Last 1
Start-Sleep 1
powershell -ExecutionPolicy Bypass -File "D:\doubao space\VioletToolBox\scripts\ui_nav4.ps1" -Name "安卓通用" -Out "D:\doubao space\VioletToolBox\p9_android.png" 2>&1 | ForEach-Object { $_.ToString() } | Select-Object -Last 1
Start-Sleep 1
powershell -ExecutionPolicy Bypass -File "D:\doubao space\VioletToolBox\scripts\ui_nav4.ps1" -Name "payload" -Out "D:\doubao space\VioletToolBox\p10_payload.png" 2>&1 | ForEach-Object { $_.ToString() } | Select-Object -Last 1
Start-Sleep 1
powershell -ExecutionPolicy Bypass -File "D:\doubao space\VioletToolBox\scripts\ui_nav4.ps1" -Name "备份助手" -Out "D:\doubao space\VioletToolBox\p11_backup.png" 2>&1 | ForEach-Object { $_.ToString() } | Select-Object -Last 1
Start-Sleep 1
powershell -ExecutionPolicy Bypass -File "D:\doubao space\VioletToolBox\scripts\ui_nav4.ps1" -Name "刷机资源" -Out "D:\doubao space\VioletToolBox\grp.png" 2>&1 | ForEach-Object { $_.ToString() } | Select-Object -Last 1
Start-Sleep 1
powershell -ExecutionPolicy Bypass -File "D:\doubao space\VioletToolBox\scripts\ui_nav4.ps1" -Name "Rom专区" -Out "D:\doubao space\VioletToolBox\p12_rom.png" 2>&1 | ForEach-Object { $_.ToString() } | Select-Object -Last 1
Start-Sleep 1
powershell -ExecutionPolicy Bypass -File "D:\doubao space\VioletToolBox\scripts\ui_nav4.ps1" -Name "下载专区" -Out "D:\doubao space\VioletToolBox\p13_download.png" 2>&1 | ForEach-Object { $_.ToString() } | Select-Object -Last 1
Start-Sleep 1
Write-Output 'ALL DONE'
