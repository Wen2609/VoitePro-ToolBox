Add-Type -AssemblyName PresentationFramework
Add-Type -AssemblyName System.Xaml

$dll = "C:\Users\Administrator\.nuget\packages\handycontrol\3.5.1\lib\net8.0\HandyControl.dll"
$outDir = "D:\doubao space\VioletToolBox\hc_templates"
New-Item -ItemType Directory -Force -Path $outDir | Out-Null

$asm = [System.Reflection.Assembly]::LoadFrom($dll)
$s = $asm.GetManifestResourceStream("HandyControl.g.resources")
$rr = New-Object System.Resources.ResourceReader($s)
$enum = $rr.GetEnumerator()
while ($enum.MoveNext()) {
    if ($enum.Key -eq "themes/skindefault.baml") {
        $stream = $enum.Value -as [System.IO.Stream]
        # .NET Framework 命名空间
        $reader = New-Object System.Windows.Baml2006.Baml2006Reader($stream)
        $obj = [System.Windows.Markup.XamlReader]::Load($reader)
        $xaml = [System.Windows.Markup.XamlWriter]::Save($obj)
        $path = Join-Path $outDir "skindefault.xaml"
        [System.IO.File]::WriteAllText($path, $xaml)
        Write-Output "Saved skindefault.xaml ($($xaml.Length) chars)"
        break
    }
}
$rr.Close()
