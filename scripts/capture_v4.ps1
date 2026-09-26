$exe = "D:\doubao space\VioletToolBox\VioletToolBox\bin\Debug\net8.0-windows\VioletToolBox.exe"
$outdir = "D:\doubao space\VioletToolBox\pages_v4"
New-Item -ItemType Directory -Force -Path $outdir | Out-Null
$cap = "D:\doubao space\VioletToolBox\scripts\cap_win.ps1"
$pages = @(
    @("BasicFlashView", "1_basic.png"),
    @("FastbootVisualizationView", "2_fastboot.png"),
    @("OujiaFlashView", "3_oujia.png"),
    @("EdlFlashView", "4_edl.png"),
    @("ColorOSAssistantView", "5_coloros.png"),
    @("HiddenEnvironmentView", "6_hidden.png"),
    @("SystemZoneView", "7_systemzone.png"),
    @("AutorootView", "8_autoroot.png"),
    @("AppManagementView", "9_appmgmt.png"),
    @("AndroidGeneralView", "10_android.png"),
    @("PayloadView", "11_payload.png"),
    @("BackupAssistantView", "12_backup.png"),
    @("RomDownloadview", "13_rom.png"),
    @("VioletDownloadView", "14_download.png"),
    @("AboutToolView", "15_about.png")
)
foreach ($pg in $pages) {
    $view = $pg[0]; $fname = $pg[1]
    $out = Join-Path $outdir $fname
    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = $exe
    $psi.Arguments = "--page=$view"
    $psi.WorkingDirectory = (Split-Path $exe)
    $psi.UseShellExecute = $true
    $proc = [System.Diagnostics.Process]::Start($psi)
    Start-Sleep 6
    $r = powershell -ExecutionPolicy Bypass -File $cap -Out $out 2>&1 | Select-Object -Last 1
    Write-Output "$view : $r"
    try { $proc.Kill() } catch { Get-Process -Name VioletToolBox -ErrorAction SilentlyContinue | ForEach-Object { try { $_.Kill() } catch {} } }
    Start-Sleep 1
}
Write-Output "ALL DONE"
