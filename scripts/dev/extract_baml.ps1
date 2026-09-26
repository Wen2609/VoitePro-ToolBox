Add-Type -AssemblyName PresentationFramework
Add-Type -AssemblyName System.Xaml

$dll = "C:\Users\Administrator\.nuget\packages\handycontrol\3.5.1\lib\net8.0\HandyControl.dll"
$outDir = "D:\doubao space\VioletToolBox\hc_templates"
New-Item -ItemType Directory -Force -Path $outDir | Out-Null

$asm = [System.Reflection.Assembly]::LoadFrom($dll)
$names = $asm.GetManifestResourceNames()
Write-Output "Resources: $($names -join ', ')"

foreach ($n in $names) {
    if (-not $n.EndsWith(".g.resources")) { continue }
    $s = $asm.GetManifestResourceStream($n)
    $rr = New-Object System.Resources.ResourceReader($s)
    $enum = $rr.GetEnumerator()
    while ($enum.MoveNext()) {
        $key = $enum.Key.ToString()
        if ($key -match "sidemenu|side_menu") {
            Write-Output "Found: $key"
            $stream = $enum.Value -as [System.IO.Stream]
            if ($stream) {
                try {
                    $reader = New-Object System.Windows.Markup.Baml2006Reader($stream)
                    $obj = [System.Windows.Markup.XamlReader]::Load($reader)
                    $xaml = [System.Windows.Markup.XamlWriter]::Save($obj)
                    $safe = $key -replace '[/\\]', '_'
                    $path = Join-Path $outDir "$safe.xaml"
                    [System.IO.File]::WriteAllText($path, $xaml)
                    Write-Output "  Saved: $safe.xaml ($($xaml.Length) chars)"
                } catch {
                    Write-Output "  Error: $($_.Exception.Message)"
                }
            }
        }
    }
    $rr.Close()
}
Write-Output "Done"
