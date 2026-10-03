param(
  [int]$TargetPid = 0,
  [string]$Out = "D:\doubao space\VioletToolBox\ui_cap.png"
)
Add-Type -AssemblyName System.Drawing
Add-Type @"
using System;
using System.Runtime.InteropServices;
using System.Collections.Generic;
public class Win32Cap2 {
  public delegate bool EnumProc(IntPtr hWnd, IntPtr lParam);
  [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc cb, IntPtr lParam);
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint pid);
  [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr hWnd);
  [DllImport("user32.dll")] public static extern int GetWindowTextW(IntPtr hWnd, System.Text.StringBuilder sb, int max);
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd, out RECT rect);
  [StructLayout(LayoutKind.Sequential)]
  public struct RECT { public int Left, Top, Right, Bottom; }
}
"@
$proc = Get-Process -Id $TargetPid -ErrorAction SilentlyContinue
if (-not $proc) { Write-Output "PROCESS NOT FOUND"; exit 1 }
$found = [IntPtr]::Zero
$cb = [Win32Cap2+EnumProc]{
  param($hWnd, $lParam)
  $pid2 = [uint32]0
  [Win32Cap2]::GetWindowThreadProcessId($hWnd, [ref]$pid2) | Out-Null
  if ($pid2 -eq [uint32]$TargetPid -and [Win32Cap2]::IsWindowVisible($hWnd)) {
    $sb = New-Object System.Text.StringBuilder 256
    [Win32Cap2]::GetWindowTextW($hWnd, $sb, 256) | Out-Null
    if ($sb.Length -gt 0) { $script:hwndFound = $hWnd; return $false }
  }
  return $true
}
[Win32Cap2]::EnumWindows($cb, [IntPtr]::Zero) | Out-Null
$hwnd = $script:hwndFound
if ($hwnd -eq $null -or $hwnd -eq [IntPtr]::Zero) { Write-Output "NO WINDOW FOUND"; exit 1 }
[Win32Cap2]::SetForegroundWindow($hwnd) | Out-Null
Start-Sleep -Milliseconds 400
$r = New-Object Win32Cap2+RECT
[Win32Cap2]::GetWindowRect($hwnd, [ref]$r) | Out-Null
$w = $r.Right - $r.Left; $h = $r.Bottom - $r.Top
Write-Output "RECT: $($r.Left),$($r.Top) ${w}x${h}"
$bmp = New-Object System.Drawing.Bitmap $w, $h
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.CopyFromScreen($r.Left, $r.Top, 0, 0, (New-Object System.Drawing.Size $w, $h))
$g.Dispose()
$bmp.Save($Out, [System.Drawing.Imaging.ImageFormat]::Png)
$bmp.Dispose()
Write-Output "SAVED $Out"
