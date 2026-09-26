# -*- coding: utf-8 -*-
import io, sys, re
sys.stdout.reconfigure(encoding='utf-8')
csfp = r'D:\doubao space\VioletToolBox\VioletToolBox\MainWindow.xaml.cs'
cs = io.open(csfp, 'r', encoding='utf-8').read()

# 1) 删 StartEdlCloudLoaderRefresh 调用（正则，容忍缩进）
pat = re.compile(r'Dispatcher\.BeginInvoke\(\s*new Action\(StartEdlCloudLoaderRefresh\),\s*System\.Windows\.Threading\.DispatcherPriority\.Background\);\s*\n(\s*)\}')
m = pat.search(cs)
assert m, 'StartEdlCloudLoaderRefresh block NOT FOUND'
cs = cs[:m.start()] + m.group(1) + '}' + cs[m.end():]
print('StartEdlCloudLoaderRefresh call removed')

# 2) 内联 3 个 EDL 分区判断方法（若不存在）
if 'internal static bool IsEdlDataPartitionLabel' not in cs:
    methods = """
        internal static bool IsEdlDataPartitionLabel(string? label)
        {
            if (string.IsNullOrWhiteSpace(label))
                return false;
            return label.Equals("userdata", StringComparison.OrdinalIgnoreCase)
                || label.Equals("metadata", StringComparison.OrdinalIgnoreCase);
        }

        internal static bool IsEdlBasebandFingerprintBackupPartitionLabel(string? label)
        {
            if (string.IsNullOrWhiteSpace(label))
                return false;

            string normalized = StripEdlSlotSuffix(label.Trim());
            if (normalized.Equals("persist", StringComparison.OrdinalIgnoreCase)
                || normalized.Equals("modemst1", StringComparison.OrdinalIgnoreCase)
                || normalized.Equals("modemst2", StringComparison.OrdinalIgnoreCase)
                || normalized.Equals("fsg", StringComparison.OrdinalIgnoreCase)
                || normalized.Equals("fsc", StringComparison.OrdinalIgnoreCase))
                return true;

            return normalized.Equals("oplusdycnvbk", StringComparison.OrdinalIgnoreCase)
                || normalized.Equals("oplusstanvbk", StringComparison.OrdinalIgnoreCase);
        }

        internal static string StripEdlSlotSuffix(string label)
        {
            if (label.EndsWith("_a", StringComparison.OrdinalIgnoreCase) ||
                label.EndsWith("_b", StringComparison.OrdinalIgnoreCase))
            {
                return label.Substring(0, label.Length - 2);
            }
            return label;
        }
"""
    anchor = "        internal static bool IsFastbootVisualizationBasebandProtectedPartitionLabel(string? partitionName)"
    assert anchor in cs, 'method insert anchor NOT FOUND'
    cs = cs.replace(anchor, methods + anchor, 1)
    print('3 partition helper methods inlined')
else:
    print('partition helpers already present')

io.open(csfp, 'w', encoding='utf-8', newline='').write(cs)
print('done')
