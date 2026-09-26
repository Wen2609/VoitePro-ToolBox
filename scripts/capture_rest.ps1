powershell -ExecutionPolicy Bypass -File "D:\doubao space\VioletToolBox\scripts\ui_nav4.ps1" -Name "实用功能" -Out "D:\doubao space\VioletToolBox\grp2.png" 2>&1 | ForEach-Object { $_.ToString() } | Select-Object -Last 1
Start-Sleep 1
powershell -ExecutionPolicy Bypass -File "D:\doubao space\VioletToolBox\scripts\ui_nav4.ps1" -Name "模块专区" -Out "D:\doubao space\VioletToolBox\p16_module.png" 2>&1 | ForEach-Object { $_.ToString() } | Select-Object -Last 1
Start-Sleep 1
powershell -ExecutionPolicy Bypass -File "D:\doubao space\VioletToolBox\scripts\ui_nav4.ps1" -Name "断点续传" -Out "D:\doubao space\VioletToolBox\p17_resume.png" 2>&1 | ForEach-Object { $_.ToString() } | Select-Object -Last 1
Start-Sleep 1
powershell -ExecutionPolicy Bypass -File "D:\doubao space\VioletToolBox\scripts\ui_nav4.ps1" -Name "文件传输" -Out "D:\doubao space\VioletToolBox\p18_file.png" 2>&1 | ForEach-Object { $_.ToString() } | Select-Object -Last 1
Start-Sleep 1
powershell -ExecutionPolicy Bypass -File "D:\doubao space\VioletToolBox\scripts\ui_nav4.ps1" -Name "脱机修补" -Out "D:\doubao space\VioletToolBox\p19_offline.png" 2>&1 | ForEach-Object { $_.ToString() } | Select-Object -Last 1
Start-Sleep 1
powershell -ExecutionPolicy Bypass -File "D:\doubao space\VioletToolBox\scripts\ui_nav4.ps1" -Name "Payload" -Out "D:\doubao space\VioletToolBox\p20_payload.png" 2>&1 | ForEach-Object { $_.ToString() } | Select-Object -Last 1
Start-Sleep 1
powershell -ExecutionPolicy Bypass -File "D:\doubao space\VioletToolBox\scripts\ui_nav4.ps1" -Name "刷机资源" -Out "D:\doubao space\VioletToolBox\grp2.png" 2>&1 | ForEach-Object { $_.ToString() } | Select-Object -Last 1
Start-Sleep 1
powershell -ExecutionPolicy Bypass -File "D:\doubao space\VioletToolBox\scripts\ui_nav4.ps1" -Name "下载专区" -Out "D:\doubao space\VioletToolBox\p13_download.png" 2>&1 | ForEach-Object { $_.ToString() } | Select-Object -Last 1
Start-Sleep 1
powershell -ExecutionPolicy Bypass -File "D:\doubao space\VioletToolBox\scripts\ui_nav4.ps1" -Name "Rom专区" -Out "D:\doubao space\VioletToolBox\p12_rom.png" 2>&1 | ForEach-Object { $_.ToString() } | Select-Object -Last 1
Start-Sleep 1
powershell -ExecutionPolicy Bypass -File "D:\doubao space\VioletToolBox\scripts\ui_nav4.ps1" -Name "刷写功能" -Out "D:\doubao space\VioletToolBox\grp2.png" 2>&1 | ForEach-Object { $_.ToString() } | Select-Object -Last 1
Start-Sleep 1
powershell -ExecutionPolicy Bypass -File "D:\doubao space\VioletToolBox\scripts\ui_nav4.ps1" -Name "降级助手" -Out "D:\doubao space\VioletToolBox\p4_coloros.png" 2>&1 | ForEach-Object { $_.ToString() } | Select-Object -Last 1
Start-Sleep 1
Write-Output 'DONE2'
