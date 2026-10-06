Add-Type -AssemblyName System.Windows.Forms, System.Drawing
$exe = "D:\doubao space\VioletToolBox\VioletToolBox\bin\Debug\net8.0-windows\VioletToolBox.exe"
$ws = New-Object -ComObject WScript.Shell
$pages = @(
    @{ p = "OujiaFlashView";  o = "c1_oujia.png" },
    @{ p = "AndroidGeneralView"; o = "c2_android.png" },
    @{ p = "EdlFlashView";    o = "c3_edl.png" },
    @{ p = "AboutToolView";   o = "c4_about.png" },
    @{ p = "VioletDownloadView"; o = "c5_dl.png" },
    @{ p = "PayloadView";     o = "c6_payload.png" },
    @{ p = "HiddenEnvironmentView"; o = "c7_hidden.png" },
    @{ p = "ScreenMirrorView"; o = "c8_mirror.png" },
    @{ p = "FastbootVisualizationView"; o = "c9_fb.png" },
    @{ p = "AIAgentView";     o = "c10_ai.png" }
)
Get-Process -Name VioletToolBox -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 2
foreach ($pg in $pages) {
    Start-Process -FilePath $exe -WorkingDirectory (Split-Path $exe) -ArgumentList "-page=$($pg.p)"
    Start-Sleep -Seconds 20
    $p = Get-Process -Name VioletToolBox -ErrorAction SilentlyContinue
    if ($p -and $p.MainWindowHandle -ne 0) {
        $null = $ws.AppActivate($p.Id)
        Start-Sleep -Milliseconds 1000
        $b = New-Object System.Drawing.Bitmap 1400, 900
        $g = [System.Drawing.Graphics]::FromImage($b)
        $g.CopyFromScreen(0, 0, 0, 0, $b.Size)
        $g.Dispose()
        $b.Save("D:\doubao space\VioletToolBox\$($pg.o)")
        "saved $($pg.o)"
    } else { "FAILED $($pg.p)" }
    Stop-Process -Name VioletToolBox -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 3
}
