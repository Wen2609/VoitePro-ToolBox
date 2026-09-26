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
public class Win32P3 {
    [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr hWnd, IntPtr hdcBlt, uint nFlags);
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd, out RECT rect);
    public struct RECT { public int Left, Top, Right, Bottom; }
}
"@
$root = [System.Windows.Automation.AutomationElement]::FromHandle($h)
$cond = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::NameProperty, $Name)
$txt = $root.FindFirst([System.Windows.Automation.TreeScope]::Descendants, $cond)
if (-not $txt) { Write-Output "text not found: $Name"; exit 1 }
# 向上找可 Invoke 的祖先
$cur = $txt
$invoked = $false
for ($i = 0; $i -lt 8; $i++) {
    $walker = [System.Windows.Automation.TreeWalker]::ControlViewWalker
    $par = $walker.GetParent($cur)
    if (-not $par) { break }
    $inv = $null
    if ($par.TryGetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern, [ref]$inv)) {
        $inv.Invoke()
        $invoked = $true
        Write-Output "invoked ancestor of $Name"
        break
    }
    $cur = $par
}
if (-not $invoked) {
    # 尝试 SelectionItem
    $cur2 = $txt
    for ($i = 0; $i -lt 8; $i++) {
        $walker = [System.Windows.Automation.TreeWalker]::ControlViewWalker
        $par = $walker.GetParent($cur2)
        if (-not $par) { break }
        $sel = $null
        if ($par.TryGetCurrentPattern([System.Windows.Automation.SelectionItemPattern]::Pattern, [ref]$sel)) {
            $sel.Select()
            $invoked = $true
            Write-Output "selected ancestor of $Name"
            break
        }
        $cur2 = $par
    }
}
if (-not $invoked) { Write-Output "could not trigger $Name"; exit 1 }
Start-Sleep 3
$r = New-Object Win32P3+RECT
[Win32P3]::GetWindowRect($h, [ref]$r) | Out-Null
$w = $r.Right - $r.Left; $hh = $r.Bottom - $r.Top
$bmp = New-Object System.Drawing.Bitmap($w, $hh)
$g = [System.Drawing.Graphics]::FromImage($bmp)
$hdc = $g.GetHdc()
[Win32P3]::PrintWindow($h, $hdc, 2) | Out-Null
$g.ReleaseHdc($hdc)
$bmp.Save($Out, [System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose(); $bmp.Dispose()
Write-Output "saved $Out ${w}x${hh}"
