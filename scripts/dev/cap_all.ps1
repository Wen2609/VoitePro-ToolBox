$pages = @(
    @("screen","screen"),
    @("basic","basic"),
    @("fastboot","fastboot"),
    @("ouga","ouga"),
    @("edl","edl"),
    @("coloros","coloros"),
    @("hidden","hidden"),
    @("violet","violet"),
    @("systemzone","systemzone"),
    @("autoroot","autoroot"),
    @("app","app"),
    @("android","android"),
    @("payload","payload"),
    @("backup","backup"),
    @("download","download"),
    @("rom","rom"),
    @("about","about")
)
foreach ($p in $pages) {
    $out = "D:\doubao space\VioletToolBox\chk_$($p[1]).png"
    & powershell -ExecutionPolicy Bypass -File "D:\doubao space\VioletToolBox\cap_page.ps1" -Page $p[0] -Out $out
    Write-Output "===== done $($p[0]) ====="
}
