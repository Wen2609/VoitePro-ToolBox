param(
    [Parameter(Mandatory=$true)][string]$Page,
    [Parameter(Mandatory=$true)][string]$Out,
    [int]$PostWait = 10
)
Add-Type -AssemblyName System.Drawing
Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
public class WinCap3 {
  [DllImport("user32.dll")] public static extern bool SetWindowPos(IntPtr h, IntPtr a, int x, int y, int cx, int cy, uint f);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
  [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr h, IntPtr dc, uint f);
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int c);
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int L, T, R, B; }
}
"@
$exe = "D:\doubao space\VioletToolBox\VioletToolBox\bin\Debug\net8.0-windows\win-x64\VioletToolBox.exe"
$wd = Split-Path $exe
$env:VTB_PAGE = $Page
$proc = Start-Process $exe -WorkingDirectory $wd -PassThru
$targetPid = $proc.Id

$h = [IntPtr]::Zero
for ($i=0; $i -lt 60; $i++) {
  Start-Sleep -Seconds 2
  $p = Get-Process -Id $targetPid -ErrorAction SilentlyContinue
  if (-not $p) { Write-Output "FAIL:进程退出 $Page"; exit 1 }
  $p.Refresh()
  $wh = $p.MainWindowHandle
  if ($wh -ne [IntPtr]::Zero) {
    $r = New-Object WinCap3+RECT
    [WinCap3]::GetWindowRect($wh,[ref]$r) | Out-Null
    if (($r.R-$r.L) -gt 200 -and ($r.B-$r.T) -gt 200) { $h = $wh; break }
  }
}
if ($h -eq [IntPtr]::Zero) { Write-Output "FAIL:未找到窗口 $Page"; Stop-Process -Id $targetPid -Force; exit 1 }

Start-Sleep -Seconds $PostWait
[WinCap3]::ShowWindow($h, 9) | Out-Null
[WinCap3]::SetWindowPos($h, [IntPtr]-1, 0,0,1000,800, 0x0002 -bor 0x0001 -bor 0x0040) | Out-Null
Start-Sleep -Milliseconds 1800
$r = New-Object WinCap3+RECT; [WinCap3]::GetWindowRect($h,[ref]$r) | Out-Null
$w = $r.R-$r.L; $hh = $r.B-$r.T
if ($w -le 100 -or $hh -le 100) { Write-Output "FAIL:窗口尺寸无效 $Page ($w x $hh)"; Stop-Process -Id $targetPid -Force; exit 1 }
$bmp = New-Object System.Drawing.Bitmap $w, $hh
$g = [System.Drawing.Graphics]::FromImage($bmp)
$hdc = $g.GetHdc(); [WinCap3]::PrintWindow($h,$hdc,2) | Out-Null; $g.ReleaseHdc($hdc)
$bmp.Save($Out, [System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose(); $bmp.Dispose()
[WinCap3]::SetWindowPos($h, [IntPtr]-2, 0,0,0,0, 0x0002 -bor 0x0001 -bor 0x0040) | Out-Null
Stop-Process -Id $targetPid -Force
Start-Sleep -Seconds 2
Write-Output "OK $Page -> $Out ($w x $hh)"
