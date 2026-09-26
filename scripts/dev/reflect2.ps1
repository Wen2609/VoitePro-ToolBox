Add-Type -AssemblyName PresentationFramework
$dll = "C:\Users\Administrator\.nuget\packages\handycontrol\3.5.1\lib\net8.0\HandyControl.dll"
$asm = [System.Reflection.Assembly]::LoadFrom($dll)
# 直接用 FullName 获取类型，避免 GetTypes 加载异常
$candidates = @(
    "HandyControl.Controls.SideMenuItem",
    "HandyControl.Controls.SideMenu",
    "HandyControl.Data.SideMenuAttach",
    "HandyControl.Tools.SideMenuAttach",
    "HandyControl.Controls.SideMenuAttach"
)
foreach ($name in $candidates) {
    $t = $asm.GetType($name, $false)
    if ($t) {
        Write-Output "=== $name ==="
        Write-Output "  Base: $($t.BaseType.FullName)"
        $t.GetProperties([System.Reflection.BindingFlags]::Public -bor [System.Reflection.BindingFlags]::Instance -bor [System.Reflection.BindingFlags]::DeclaredOnly) | ForEach-Object { Write-Output "  Prop: $($_.Name) : $($_.PropertyType.Name)" }
        $t.GetFields([System.Reflection.BindingFlags]::Public -bor [System.Reflection.BindingFlags]::Static -bor [System.Reflection.BindingFlags]::DeclaredOnly) | Where-Object { $_.Name -match "Property|Attach" } | ForEach-Object { Write-Output "  Field: $($_.Name)" }
    } else {
        Write-Output "NOT FOUND: $name"
    }
}
