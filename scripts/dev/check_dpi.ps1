Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
public class Dpi {
  [DllImport("user32.dll")] public static extern IntPtr GetDC(IntPtr h);
  [DllImport("gdi32.dll")] public static extern int GetDeviceCaps(IntPtr hdc, int i);
  [DllImport("user32.dll")] public static extern int ReleaseDC(IntPtr h, IntPtr hdc);
  [DllImport("user32.dll")] public static extern uint GetDpiForWindow(IntPtr h);
}
"@
$dc = [Dpi]::GetDC([IntPtr]::Zero)
$dpiX = [Dpi]::GetDeviceCaps($dc, 88)
[Dpi]::ReleaseDC([IntPtr]::Zero, $dc) | Out-Null
Write-Output ("System DPI X: " + $dpiX + "  scale: " + ($dpiX/96))
# 运行中的 VioletToolBox 窗口 DPI
$p = Get-Process -Name VioletToolBox -ErrorAction SilentlyContinue | Select-Object -First 1
if ($p) {
  $p.Refresh()
  $wdpi = [Dpi]::GetDpiForWindow($p.MainWindowHandle)
  Write-Output ("Window DPI: " + $wdpi + "  scale: " + ($wdpi/96))
  $r = New-Object Object
  Add-Member -InputObject $r -NotePropertyName L -NotePropertyValue 0
}
