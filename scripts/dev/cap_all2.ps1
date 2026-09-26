param(
    [string]$OutDir = "D:\doubao space\VioletToolBox\all_pages",
    [int]$PageGap = 5
)
Add-Type -AssemblyName System.Drawing
Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
public class WinCapA {
  [DllImport("user32.dll")] public static extern bool SetWindowPos(IntPtr h, IntPtr a, int x, int y, int cx, int cy, uint f);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
  [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr h, IntPtr dc, uint f);
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int c);
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int L, T, R, B; }
}
"@
$pages = @("screen","basic","fastboot","ouga","edl","coloros","hidden","violet","systemzone","autoroot","app","android","payload","backup","download","rom","about")
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
$sigFile = "D:\doubao space\VioletToolBox\vtb_cur.txt"
$errFile = "D:\doubao space\VioletToolBox\vtb_err.txt"
Remove-Item $sigFile,$errFile -ErrorAction SilentlyContinue

$exe = "D:\doubao space\VioletToolBox\VioletToolBox\bin\Debug\net8.0-windows\win-x64\VioletToolBox.exe"
$env:VTB_PAGE = "all"
$proc = Start-Process $exe -WorkingDirectory (Split-Path $exe) -PassThru
$targetPid = $proc.Id

$h = [IntPtr]::Zero
for ($i=0; $i -lt 75; $i++) {
  Start-Sleep -Seconds 2
  $p = Get-Process -Id $targetPid -ErrorAction SilentlyContinue
  if (-not $p) { Write-Output "FAIL:进程退出"; exit 1 }
  $p.Refresh()
  if ($p.MainWindowHandle -ne [IntPtr]::Zero) { $h = $p.MainWindowHandle; break }
}
if ($h -eq [IntPtr]::Zero) { Write-Output "FAIL:无窗口"; Stop-Process -Id $targetPid -Force; exit 1 }
[WinCapA]::ShowWindow($h, 9) | Out-Null
[WinCapA]::SetWindowPos($h, [IntPtr]-1, 0,0,1000,800, 0x0002 -bor 0x0001 -bor 0x0040) | Out-Null
Start-Sleep -Milliseconds 800

function Shot($wh, $path) {
  $r = New-Object WinCapA+RECT; [WinCapA]::GetWindowRect($wh,[ref]$r) | Out-Null
  $w = $r.R-$r.L; $hh = $r.B-$r.T
  $bmp = New-Object System.Drawing.Bitmap $w, $hh
  $g = [System.Drawing.Graphics]::FromImage($bmp)
  $hdc = $g.GetHdc(); [WinCapA]::PrintWindow($wh,$hdc,2) | Out-Null; $g.ReleaseHdc($hdc)
  $bmp.Save($path, [System.Drawing.Imaging.ImageFormat]::Png)
  $g.Dispose(); $bmp.Dispose()
}

$done = 0
$deadline = (Get-Date).AddSeconds(360)
while ($done -lt $pages.Count -and (Get-Date) -lt $deadline) {
  if (Test-Path $errFile) { Write-Output "ERR: $(Get-Content $errFile -Raw)"; break }
  if (Test-Path $sigFile) {
    $sig = (Get-Content $sigFile -Raw).Trim()
    $parts = $sig.Split(":")
    $idx = [int]$parts[0]; $key = $parts[1]
    if ($idx -eq $done) {
      Start-Sleep -Milliseconds 2600
      $p = Get-Process -Id $targetPid -ErrorAction SilentlyContinue
      if ($p) { $p.Refresh(); $h = $p.MainWindowHandle }
      $path = Join-Path $OutDir ("{0:D2}_{1}.png" -f $idx, $key)
      Shot $h $path
      Write-Output "[$($idx+1)/$($pages.Count)] $key -> $path"
      $done++
    }
  }
  Start-Sleep -Milliseconds 300
}
Stop-Process -Id $targetPid -Force -ErrorAction SilentlyContinue
Write-Output "DONE: $done / $($pages.Count) 页"
