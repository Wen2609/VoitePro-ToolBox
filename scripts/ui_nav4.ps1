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
Add-Type -AssemblyName System.Windows.Forms
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class Win32P5 {
    [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr hWnd, IntPtr hdcBlt, uint nFlags);
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd, out RECT rect);
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
    [StructLayout(LayoutKind.Sequential)] public struct RECT { public int Left, Top, Right, Bottom; }
}
"@
# 恢复窗口
[Win32P5]::ShowWindow($h, 9) | Out-Null   # SW_RESTORE
[Win32P5]::SetForegroundWindow($h) | Out-Null
Start-Sleep 2
$root = [System.Windows.Automation.AutomationElement]::FromHandle($h)
$cond = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::NameProperty, $Name)
$txt = $root.FindFirst([System.Windows.Automation.TreeScope]::Descendants, $cond)
if (-not $txt) { Write-Output "text not found: $Name"; exit 1 }
$rect = $txt.Current.BoundingRectangle
if ($rect.IsEmpty) { Write-Output "no bounding rect"; exit 1 }
$cx = [int]($rect.X + $rect.Width / 2)
$cy = [int]($rect.Y + $rect.Height / 2)
Write-Output "clicking $Name at $cx,$cy"
[System.Windows.Forms.Cursor]::Position = New-Object System.Drawing.Point($cx, $cy)
Start-Sleep 0.3
[Win32P5]::SetForegroundWindow($h) | Out-Null
Start-Sleep 0.5
Add-Type -AssemblyName Microsoft.VisualBasic
[Microsoft.VisualBasic.Interaction]::AppActivate($p.Id) | Out-Null
Start-Sleep 0.3
# 模拟点击
[System.Windows.Forms.SendKeys]::SendWait("{ENTER}") | Out-Null
Start-Sleep 0.3
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class MouseP {
    [DllImport("user32.dll")] public static extern void mouse_event(uint dwFlags, int dx, int dy, uint dwData, UIntPtr dwExtraInfo);
}
"@
[MouseP]::mouse_event(0x0002, 0, 0, 0, [UIntPtr]::Zero)
[MouseP]::mouse_event(0x0004, 0, 0, 0, [UIntPtr]::Zero)
Start-Sleep 3
$r = New-Object Win32P5+RECT
[Win32P5]::GetWindowRect($h, [ref]$r) | Out-Null
$w = $r.Right - $r.Left; $hh = $r.Bottom - $r.Top
if ($w -le 100) { Write-Output "window still hidden ${w}x${hh}"; exit 1 }
$bmp = New-Object System.Drawing.Bitmap($w, $hh)
$g = [System.Drawing.Graphics]::FromImage($bmp)
$hdc = $g.GetHdc()
[Win32P5]::PrintWindow($h, $hdc, 2) | Out-Null
$g.ReleaseHdc($hdc)
$bmp.Save($Out, [System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose(); $bmp.Dispose()
Write-Output "saved $Out ${w}x${hh}"
