# VioletToolBox: token-ize hardcoded palette hexes in MainWindow.xaml
# - Adds TextMutedBrush + BorderSubtleBrush to Colors.xaml
# - Replaces safe non-animation patterns with StaticResource refs
# Preserves LF, no BOM.

$ErrorActionPreference = "Stop"

$colorsPath = "D:\doubao space\VioletToolBox\VioletToolBox\Themes\Colors.xaml"
$mainPath = "D:\doubao space\VioletToolBox\VioletToolBox\MainWindow.xaml"

# ---- 1. Add token resources if missing ----
$colors = [System.IO.File]::ReadAllText($colorsPath)
$added = @()
if (-not $colors.Contains("TextMutedBrush")) {
    $colors = $colors.Replace(
        '<SolidColorBrush x:Key="TextTertiaryBrush" Color="{StaticResource Gray400}"/>',
        '<SolidColorBrush x:Key="TextMutedBrush" Color="{StaticResource Gray500}"/>' + "`n" + '    <SolidColorBrush x:Key="TextTertiaryBrush" Color="{StaticResource Gray400}"/>')
    $added += "TextMutedBrush"
}
if (-not $colors.Contains("BorderSubtleBrush")) {
    $colors = $colors.Replace(
        '<SolidColorBrush x:Key="BorderBrush" Color="{StaticResource Gray200}"/>',
        '<SolidColorBrush x:Key="BorderSubtleBrush" Color="{StaticResource Gray100}"/>' + "`n" + '    <SolidColorBrush x:Key="BorderBrush" Color="{StaticResource Gray200}"/>')
    $added += "BorderSubtleBrush"
}
$colors = $colors -replace "`r`n", "`n"
[System.IO.File]::WriteAllText($colorsPath, $colors, (New-Object System.Text.UTF8Encoding($false)))
"Colors.xaml tokens added: " + ($added -join ", ")

# ---- 2. Safe pattern replacements (non-animation contexts only) ----
$t = [System.IO.File]::ReadAllText($mainPath)
$stats = @()
function Replace-Pattern([string]$content, [string]$pattern, [string]$replacement, [string]$label) {
    $count = ([regex]::Matches($content, [regex]::Escape($pattern))).Count
    if ($count -gt 0) {
        $content = $content.Replace($pattern, $replacement)
        $script:stats += "$label=$count"
    }
    return $content
}

# Page headers: icon badge background -> BrandPrimaryBrush
$t = Replace-Pattern $t 'Background="#FF007AFF"' 'Background="{StaticResource BrandPrimaryBrush}"' "BrandBlue"
# Secondary text (subtitles/labels) -> TextMutedBrush
$t = Replace-Pattern $t 'Foreground="#FF8E8E93"' 'Foreground="{StaticResource TextMutedBrush}"' "MutedText"
# Primary ink text -> TextPrimaryBrush
$t = Replace-Pattern $t 'Foreground="#FF1D1D1F"' 'Foreground="{StaticResource TextPrimaryBrush}"' "InkText"
# Subtle card borders -> BorderSubtleBrush
$t = Replace-Pattern $t 'BorderBrush="#FFE5E5EA"' 'BorderBrush="{StaticResource BorderSubtleBrush}"' "SubtleBorder"
# Selection tint backgrounds (Setter/element only, not animation To=) -> BrandTintBrush
$t = Replace-Pattern $t 'Background="#FFE8F0FF"' 'Background="{StaticResource BrandTintBrush}"' "TintBg"

$t = $t -replace "`r`n", "`n"
[System.IO.File]::WriteAllText($mainPath, $t, (New-Object System.Text.UTF8Encoding($false)))
"Replacements: " + ($stats -join ", ")
