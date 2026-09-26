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
public class Win32P6 {
    [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr hWnd, IntPtr hdcBlt, uint nFlags);
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd, out RECT rect);
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern bool SetWindowPos(IntPtr hWnd, IntPtr after, int x, int y, int cx, int cy, uint flags);
    [StructLayout(LayoutKind.Sequential)] public struct RECT { public int Left, Top, Right, Bottom; }
}
"@
# 恢复 + 前置 + 等待
[Win32P6]::ShowWindow($h, 9) | Out-Null
Start-Sleep 0.5
# 居中到屏幕（SWP_NOSIZE=1, SWP_NOZORDER=4）
$sw = [System.Windows.Forms.Screen]::PrimaryScreen.WorkingArea
[Win32P6]::SetWindowPos($h, [IntPtr]::Zero, [int](($sw.Width-1010)/2), [int](($sw.Height-800)/2), 0, 0, 5) | Out-Null
Start-Sleep 0.5
[Win32P6]::SetForegroundWindow($h) | Out-Null
Start-Sleep 1
function Click-El($el) {
    $r = $el.Current.BoundingRectangle
    if ($r.IsEmpty) { return $false }
    $cx = [int]($r.X + $r.Width / 2); $cy = [int]($r.Y + $r.Height / 2)
    [System.Windows.Forms.Cursor]::Position = New-Object System.Drawing.Point($cx, $cy)
    Start-Sleep 0.2
    [Win32P6]::SetForegroundWindow($h) | Out-Null
    Start-Sleep 0.2
    [System.Windows.Forms.SendKeys]::SendWait("{ENTER}") | Out-Null
    Start-Sleep 0.2
    Add-Type @"
using System;
using System.Runtime.InteropServices;
public class MouseP2 {
    [DllImport("user32.dll")] public static extern void mouse_event(uint dwFlags, int dx, int dy, uint dwData, UIntPtr dwExtraInfo);
}
"@
    [MouseP2]::mouse_event(0x0002, 0, 0, 0, [UIntPtr]::Zero)
    [MouseP2]::mouse_event(0x0004, 0, 0, 0, [UIntPtr]::Zero)
    return $true
}
if (-not (Click-El $txt)) { Write-Output "no rect: $Name"; exit 1 }

$root = [System.Windows.Automation.AutomationElement]::FromHandle($h)
function Find-ByName([string]$nm) {
    $cond = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::NameProperty, $nm)
    return $root.FindFirst([System.Windows.Automation.TreeScope]::Descendants, $cond)
}
$txt = Find-ByName $Name
if (-not $txt) {
    $groupMap = @{
        "基本刷入" = "刷写功能"; "可视刷写" = "刷写功能"; "欧加线刷" = "刷写功能";
        "EDL刷写" = "刷写功能"; "降级助手" = "刷写功能";
        "隐藏环境" = "实用功能"; "系统分区" = "实用功能"; "自动root" = "实用功能";
        "应用管理" = "实用功能"; "安卓通用" = "实用功能";
        "payload" = "刷机资源"; "Rom专区" = "刷机资源"; "下载专区" = "刷机资源";
        "备份助手" = "刷机资源"
    }
    $grp = $groupMap[$Name]
    if ($grp) {
        $g = Find-ByName $grp
        if ($g) { Click-El $g; Start-Sleep 1 }
        $txt = Find-ByName $Name
    }
}
if (-not $txt) {
    Write-Output "not found: $Name (group may be collapsed)"
    exit 2
}
Start-Sleep 3
$r = New-Object Win32P6+RECT
[Win32P6]::GetWindowRect($h, [ref]$r) | Out-Null
$w = $r.Right - $r.Left; $hh = $r.Bottom - $r.Top
if ($w -le 100) { Write-Output "window hidden ${w}x${hh}"; exit 1 }
$bmp = New-Object System.Drawing.Bitmap($w, $hh)
$g = [System.Drawing.Graphics]::FromImage($bmp)
$hdc = $g.GetHdc()
[Win32P6]::PrintWindow($h, $hdc, 2) | Out-Null
$g.ReleaseHdc($hdc)
$bmp.Save($Out, [System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose(); $bmp.Dispose()
Write-Output "saved $Out ${w}x${hh}"
