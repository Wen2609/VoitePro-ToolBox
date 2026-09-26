param(
    [Parameter(Mandatory=$true)][string]$Page,
    [Parameter(Mandatory=$true)][string]$Out
)
Add-Type -AssemblyName System.Drawing
Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
public class WinCap {
  [DllImport("user32.dll")] public static extern bool SetWindowPos(IntPtr h, IntPtr a, int x, int y, int cx, int cy, uint f);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
  [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr h, IntPtr dc, uint f);
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int L, T, R, B; }
}
"@
$exe = "D:\doubao space\VioletToolBox\VioletToolBox\bin\Debug\net8.0-windows\win-x64\VioletToolBox.exe"
$wd = Split-Path $exe
$env:VTB_PAGE = $Page
$proc = Start-Process $exe -WorkingDirectory $wd -PassThru
Start-Sleep -Seconds 55
$p = Get-Process -Id $proc.Id -ErrorAction SilentlyContinue
if (-not $p) { Write-Output "FAIL:进程退出 $Page"; exit 1 }
$h = $p.MainWindowHandle
[WinCap]::SetWindowPos($h, [IntPtr]-1, 0,0,0,0, 0x0002 -bor 0x0001 -bor 0x0040) | Out-Null
Start-Sleep -Milliseconds 1500
$w = 0; $hh = 0
for ($i=0; $i -lt 8; $i++) {
    $r = New-Object WinCap+RECT; [WinCap]::GetWindowRect($h, [ref]$r) | Out-Null
    $w = $r.R - $r.L; $hh = $r.B - $r.T
    if ($w -gt 100 -and $hh -gt 100) { break }
    Start-Sleep -Milliseconds 1200
}
if ($w -le 100 -or $hh -le 100) { Write-Output "FAIL:窗口尺寸无效 $Page ($w x $hh)"; Stop-Process -Id $proc.Id -Force; exit 1 }
$bmp = New-Object System.Drawing.Bitmap $w, $hh
$g = [System.Drawing.Graphics]::FromImage($bmp)
$hdc = $g.GetHdc(); [WinCap]::PrintWindow($h, $hdc, 2) | Out-Null; $g.ReleaseHdc($hdc)
$bmp.Save($Out, [System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose(); $bmp.Dispose()
[WinCap]::SetWindowPos($h, [IntPtr]-2, 0,0,0,0, 0x0002 -bor 0x0001 -bor 0x0040) | Out-Null
Stop-Process -Id $proc.Id -Force
Start-Sleep -Seconds 2
Write-Output "OK $Page -> $Out"
