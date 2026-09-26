Add-Type -AssemblyName PresentationFramework
$dll = "C:\Users\Administrator\.nuget\packages\handycontrol\3.5.1\lib\net8.0\HandyControl.dll"
$asm = [System.Reflection.Assembly]::LoadFrom($dll)
$types = $asm.GetTypes() | Where-Object { $_.Name -match "SideMenu" }
$types | ForEach-Object { Write-Output "$($_.FullName) (base: $($_.BaseType.Name))" }
