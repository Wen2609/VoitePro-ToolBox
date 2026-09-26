param(
    [string]$Name = "基本刷入",
    [string]$Out = "D:\doubao space\VioletToolBox\page_check.png"
)
$p = Get-Process -Name VioletToolBox -ErrorAction SilentlyContinue
if (-not $p) { Write-Output "GONE"; exit 1 }
$h = $p.MainWindowHandle
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
Add-Type -AssemblyName System.Drawing
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class Win32P4 {
    [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr hWnd, IntPtr hdcBlt, uint nFlags);
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd, out RECT rect);
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern void mouse_event(uint dwFlags, uint dx, uint dy, uint dwData, UIntPtr dwExtraInfo);
    public struct RECT { public int Left, Top, Right, Bottom; }
}
"@
# 前台
[Win32P4]::SetForegroundWindow($h) | Out-Null
Start-Sleep 1
$root = [System.Windows.Automation.AutomationElement]::FromHandle($h)
$cond = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::NameProperty, $Name)
$txt = $root.FindFirst([System.Windows.Automation.TreeScope]::Descendants, $cond)
if (-not $txt) { Write-Output "text not found: $Name"; exit 1 }
$rect = $txt.Current.BoundingRectangle
if ($rect.IsEmpty) { Write-Output "no bounding rect"; exit 1 }
$cx = [int]($rect.X + $rect.Width / 2)
$cy = [int]($rect.Y + $rect.Height / 2)
Write-Output "clicking $Name at $cx,$cy"
[Win32P4]::mouse_event(0x0002, $cx, $cy, 0, [UIntPtr]::Zero)   # LEFTDOWN
[Win32P4]::mouse_event(0x0004, $cx, $cy, 0, [UIntPtr]::Zero)   # LEFTUP
Start-Sleep 3
$r = New-Object Win32P4+RECT
[Win32P4]::GetWindowRect($h, [ref]$r) | Out-Null
$w = $r.Right - $r.Left; $hh = $r.Bottom - $r.Top
$bmp = New-Object System.Drawing.Bitmap($w, $hh)
$g = [System.Drawing.Graphics]::FromImage($bmp)
$hdc = $g.GetHdc()
[Win32P4]::PrintWindow($h, $hdc, 2) | Out-Null
$g.ReleaseHdc($hdc)
$bmp.Save($Out, [System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose(); $bmp.Dispose()
Write-Output "saved $Out ${w}x${hh}"
