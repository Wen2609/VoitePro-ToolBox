$pages = @('home','basic','fastboot','ouga','edl','coloros','hidden','violet','systemzone','autoroot','app','android','payload','backup','download','rom','about')
$exe = "D:\doubao space\VioletToolBox\VioletToolBox\bin\Debug\net8.0-windows\VioletToolBox.exe"
$outdir = "D:\doubao space\VioletToolBox\pages_scan"
New-Item -ItemType Directory -Force -Path $outdir | Out-Null

Add-Type -AssemblyName System.Drawing
Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
public class CapS {
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
  [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr h, IntPtr dc, uint f);
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int L, T, R, B; }
}
"@

foreach ($page in $pages) {
  Get-Process VioletToolBox -ErrorAction SilentlyContinue | Stop-Process -Force
  Start-Sleep 2
  $env:VTB_PAGE = $page
  $p = Start-Process $exe -WorkingDirectory (Split-Path $exe) -PassThru
  # 等待窗口
  $h = [IntPtr]::Zero
  for ($i=0; $i -lt 12; $i++) {
    Start-Sleep 4
    $proc = Get-Process -Id $p.Id -ErrorAction SilentlyContinue
    if (-not $proc) { break }
    if ($proc.MainWindowHandle -ne 0) { $h = $proc.MainWindowHandle; break }
  }
  if ($h -ne [IntPtr]::Zero) {
    Start-Sleep 1
    $r = New-Object CapS+RECT; [CapS]::GetWindowRect($h,[ref]$r) | Out-Null
    $w=$r.R-$r.L; $hh=$r.B-$r.T
    $bmp = New-Object System.Drawing.Bitmap $w,$hh
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    $hdc = $g.GetHdc(); [CapS]::PrintWindow($h,$hdc,2) | Out-Null; $g.ReleaseHdc($hdc)
    $bmp.Save("$outdir\$page.png",[System.Drawing.Imaging.ImageFormat]::Png)
    $g.Dispose(); $bmp.Dispose()
    Write-Output "$page OK"
  } else {
    Write-Output "$page FAIL"
  }
}
Remove-Item Env:\VTB_PAGE -ErrorAction SilentlyContinue
