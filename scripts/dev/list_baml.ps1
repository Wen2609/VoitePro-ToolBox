Add-Type -AssemblyName PresentationFramework
Add-Type -AssemblyName System.Xaml

$dll = "C:\Users\Administrator\.nuget\packages\handycontrol\3.5.1\lib\net8.0\HandyControl.dll"
$outDir = "D:\doubao space\VioletToolBox\hc_templates"
New-Item -ItemType Directory -Force -Path $outDir | Out-Null

$asm = [System.Reflection.Assembly]::LoadFrom($dll)
$s = $asm.GetManifestResourceStream("HandyControl.g.resources")
$rr = New-Object System.Resources.ResourceReader($s)
$enum = $rr.GetEnumerator()
$all = @()
while ($enum.MoveNext()) {
    $all += $enum.Key.ToString()
}
$rr.Close()
Write-Output "Total keys: $($all.Count)"
$all | Where-Object { $_ -match "theme|generic|style|control" } | ForEach-Object { Write-Output $_ }
Write-Output "---ALL BAML---"
$all | Where-Object { $_ -match "\.baml" } | ForEach-Object { Write-Output $_ }
