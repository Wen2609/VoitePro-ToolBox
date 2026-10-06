Add-Type -AssemblyName System.Drawing
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class WinCap {
    [DllImport("user32.dll")]
    public static extern bool PrintWindow(IntPtr hwnd, IntPtr hdcBlt, uint nFlags);
    [DllImport("user32.dll")]
    public static extern bool GetWindowRect(IntPtr hWnd, out RECT lpRect);
    [StructLayout(LayoutKind.Sequential)]
    public struct RECT { public int Left, Top, Right, Bottom; }
}
"@
$exe = "D:\doubao space\VioletToolBox\VioletToolBox\bin\Debug\net8.0-windows\VioletToolBox.exe"
$pages = @(
    @{ p = "HomeView";          o = "w1_home.png" },
    @{ p = "AIAgentView";       o = "w2_ai.png" },
    @{ p = "HiddenEnvironmentView"; o = "w3_hidden.png" },
    @{ p = "SystemZoneView";    o = "w4_sz.png" },
    @{ p = "AppManagementView"; o = "w5_app.png" },
    @{ p = "AndroidGeneralView";o = "w6_android.png" },
    @{ p = "EdlFlashView";      o = "w7_edl.png" },
    @{ p = "AboutToolView";     o = "w8_about.png" },
    @{ p = "BasicFlashView";    o = "w9_basic.png" },
    @{ p = "ScreenMirrorView";  o = "w10_mirror.png" },
    @{ p = "FastbootVisualizationView"; o = "w11_fb.png" },
    @{ p = "OugaFlashView";     o = "w12_oujia.png" },
    @{ p = "VioletDownloadView";o = "w13_dl.png" },
    @{ p = "PayloadView";       o = "w14_payload.png" }
)
Get-Process -Name VioletToolBox -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 2
foreach ($pg in $pages) {
    Start-Process -FilePath $exe -WorkingDirectory (Split-Path $exe) -ArgumentList "-page=$($pg.p)"
    Start-Sleep -Seconds 20
    $p = Get-Process -Name VioletToolBox -ErrorAction SilentlyContinue
    if ($p -and $p.MainWindowHandle -ne 0) {
        $hwnd = $p.MainWindowHandle
        $rect = New-Object WinCap+RECT
        [WinCap]::GetWindowRect($hwnd, [ref]$rect) | Out-Null
        $w = $rect.Right - $rect.Left; $h = $rect.Bottom - $rect.Top
        if ($w -gt 100 -and $h -gt 100) {
            $bmp = New-Object System.Drawing.Bitmap $w, $h
            $g = [System.Drawing.Graphics]::FromImage($bmp)
            $hdc = $g.GetHdc()
            [WinCap]::PrintWindow($hwnd, $hdc, 2) | Out-Null
            $g.ReleaseHdc($hdc)
            $g.Dispose()
            $bmp.Save("D:\doubao space\VioletToolBox\$($pg.o)")
            "saved $($pg.o) (${w}x${h})"
        } else { "bad-rect $($pg.p) ${w}x${h}" }
    } else { "FAILED $($pg.p)" }
    Stop-Process -Name VioletToolBox -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 3
}
