Add-Type -AssemblyName System.Drawing
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class WCap3 {
    [DllImport("user32.dll")]
    public static extern bool PrintWindow(IntPtr hwnd, IntPtr hdcBlt, uint nFlags);
    [DllImport("user32.dll")]
    public static extern bool GetWindowRect(IntPtr hWnd, out RECT lpRect);
    [StructLayout(LayoutKind.Sequential)]
    public struct RECT { public int Left, Top, Right, Bottom; }
}
"@
$exe = "D:\doubao space\VioletToolBox\VioletToolBox\bin\Debug\net8.0-windows\VioletToolBox.exe"
Get-Process -Name VioletToolBox -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 2
Start-Process -FilePath $exe -WorkingDirectory (Split-Path $exe)
Start-Sleep -Seconds 24
$p = Get-Process -Name VioletToolBox -ErrorAction SilentlyContinue
if ($p -and $p.MainWindowHandle -ne 0) {
    $hwnd = $p.MainWindowHandle
    $rect = New-Object WCap3+RECT
    [WCap3]::GetWindowRect($hwnd, [ref]$rect) | Out-Null
    $w = $rect.Right - $rect.Left; $h = $rect.Bottom - $rect.Top
    if ($w -gt 100 -and $h -gt 100) {
        $bmp = New-Object System.Drawing.Bitmap $w, $h
        $g = [System.Drawing.Graphics]::FromImage($bmp)
        $hdc = $g.GetHdc()
        [WCap3]::PrintWindow($hwnd, $hdc, 2) | Out-Null
        $g.ReleaseHdc($hdc)
        $g.Dispose()
        $bmp.Save("D:\doubao space\VioletToolBox\ui_final_home.png")
        "saved ${w}x${h}"
    } else { "bad-rect ${w}x${h}" }
} else { "FAILED" }
Stop-Process -Name VioletToolBox -Force -ErrorAction SilentlyContinue
