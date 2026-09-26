Add-Type -AssemblyName PresentationFramework
$dll = "C:\Users\Administrator\.nuget\packages\handycontrol\3.5.1\lib\net8.0\HandyControl.dll"
$asm = [System.Reflection.Assembly]::LoadFrom($dll)
$t = $asm.GetType("HandyControl.Controls.SideMenuItem")
Write-Output "=== Type: $($t.FullName) ==="
Write-Output "Base: $($t.BaseType.FullName)"
Write-Output "=== TemplatePart attributes ==="
$t.GetCustomAttributes($false) | Where-Object { $_.TypeId.Name -match "TemplatePart" } | ForEach-Object { Write-Output "  Name=$($_.Name) Type=$($_.Type)" }
Write-Output "=== Properties (declared) ==="
$t.GetProperties([System.Reflection.BindingFlags]::Public -bor [System.Reflection.BindingFlags]::Instance -bor [System.Reflection.BindingFlags]::DeclaredOnly) | ForEach-Object { Write-Output "  $($_.Name) : $($_.PropertyType.Name)" }
Write-Output "=== Fields (declared, public/protected) ==="
$t.GetFields([System.Reflection.BindingFlags]::Public -bor [System.Reflection.BindingFlags]::NonPublic -bor [System.Reflection.BindingFlags]::Static -bor [System.Reflection.BindingFlags]::DeclaredOnly) | Where-Object { $_.Name -match "PART|Element" } | ForEach-Object { Write-Output "  $($_.Name)" }
