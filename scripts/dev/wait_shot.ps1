param(
  [Parameter(Mandatory=$true)][int]$WaitIdx,
  [Parameter(Mandatory=$true)][string]$Out
)
Add-Type -AssemblyName System.Drawing
Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
public class WinCapW {
  [DllImport("user32.dll")] public static extern bool SetWindowPos(IntPtr h, IntPtr a, int x, int y, int cx, int cy, uint f);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
  [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr h, IntPtr dc, uint f);
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int c);
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int L,T,R,B; }
}
"@
$exe = "D:\doubao space\VioletToolBox\VioletToolBox\bin\Debug\net8.0-windows\VioletToolBox.exe"
$wd = Split-Path $exe
$sigFile = "D:\doubao space\VioletToolBox\vtb_cur.txt"
$env:VTB_PAGE = "all"
Remove-Item $sigFile -ErrorAction SilentlyContinue
$proc = Start-Process $exe -WorkingDirectory $wd -PassThru
$id = $proc.Id
$h = [IntPtr]::Zero
for ($i=0; $i -lt 90; $i++) {
  Start-Sleep -Seconds 2
  $p = Get-Process -Id $id -ErrorAction SilentlyContinue
  if (-not $p) { Write-Output "FAIL:进程退出"; exit 1 }
  $p.Refresh()
  if ($p.MainWindowHandle -ne [IntPtr]::Zero) { $h = $p.MainWindowHandle; break }
}
if ($h -eq [IntPtr]::Zero) { Write-Output "FAIL:无窗口"; Stop-Process -Id $id -Force; exit 1 }
[WinCapW]::ShowWindow($h,9) | Out-Null
[WinCapW]::SetWindowPos($h,[IntPtr]-1,0,0,1000,800,0x0002 -bor 0x0001 -bor 0x0040) | Out-Null

# 等待到达目标页（信号 idx:key）
$target = "$($WaitIdx):"
$ok = $false
for ($i=0; $i -lt 120; $i++) {
  if (Test-Path $sigFile) {
    $s = (Get-Content $sigFile -Raw).Trim()
    if ($s.StartsWith($target)) { $ok=$true; break }
  }
  Start-Sleep -Milliseconds 500
}
if (-not $ok) { Write-Output "FAIL:未到达页 $WaitIdx (cur=$(Get-Content $sigFile -Raw -ErrorAction SilentlyContinue))"; Stop-Process -Id $id -Force; exit 1 }
Start-Sleep -Milliseconds 3200
$p = Get-Process -Id $id; $p.Refresh(); $h=$p.MainWindowHandle
$r = New-Object WinCapW+RECT; [WinCapW]::GetWindowRect($h,[ref]$r) | Out-Null
$w=$r.R-$r.L; $hh=$r.B-$r.T
$bmp = New-Object System.Drawing.Bitmap $w,$hh
$g=[System.Drawing.Graphics]::FromImage($bmp)
$hdc=$g.GetHdc(); [WinCapW]::PrintWindow($h,$hdc,2)|Out-Null; $g.ReleaseHdc($hdc)
$bmp.Save($Out,[System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose(); $bmp.Dispose()
Write-Output "OK page=$WaitIdx cur=$(Get-Content $sigFile -Raw) -> $Out"
Stop-Process -Id $id -Force -ErrorAction SilentlyContinue
