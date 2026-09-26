$p = Get-Process -Name VioletToolBox -ErrorAction SilentlyContinue
if (-not $p) { Write-Output "GONE"; exit 1 }
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
$root = [System.Windows.Automation.AutomationElement]::FromHandle($p.MainWindowHandle)
# 枚举所有 Name 非空的元素（前 60 个）
$all = $root.FindAll([System.Windows.Automation.TreeScope]::Descendants, [System.Windows.Automation.Condition]::TrueCondition)
$n = 0
foreach ($e in $all) {
    $nm = $e.Current.Name
    $id = $e.Current.AutomationId
    $ct = $e.Current.ControlType.ProgrammaticName
    if ($nm) {
        Write-Output ("{0} | {1} | {2}" -f $nm, $id, $ct)
        $n++
        if ($n -ge 70) { break }
    }
}
