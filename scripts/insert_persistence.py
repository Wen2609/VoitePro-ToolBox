# -*- coding: utf-8 -*-
"""插入 4 个状态持久化方法到 ToggleGroup 前"""
import io, sys
sys.stdout.reconfigure(encoding='utf-8')
p = r'D:\doubao space\VioletToolBox\VioletToolBox\MainWindow.xaml.cs'
c = io.open(p, 'r', encoding='utf-8').read()

anchor = '        private void ToggleGroup(string groupName, bool? expand = null)'
methods = '''        private void RestoreWindowState()
        {
            try
            {
                var dir = System.IO.Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "VioletToolBox");
                var file = System.IO.Path.Combine(dir, "window_state.txt");
                if (!System.IO.File.Exists(file)) return;
                double left = 0, top = 0, width = 1000, height = 850;
                foreach (var ln in System.IO.File.ReadAllLines(file))
                {
                    var kv = ln.Split('=');
                    if (kv.Length != 2) continue;
                    if (double.TryParse(kv[1], out var v))
                    {
                        if (kv[0] == "Left") left = v;
                        else if (kv[0] == "Top") top = v;
                        else if (kv[0] == "Width") width = v;
                        else if (kv[0] == "Height") height = v;
                    }
                }
                var wa = SystemParameters.WorkArea;
                width = Math.Min(Math.Max(width, MinWidth), wa.Width);
                height = Math.Min(Math.Max(height, MinHeight), wa.Height);
                left = Math.Max(wa.Left, Math.Min(left, wa.Right - width));
                top = Math.Max(wa.Top, Math.Min(top, wa.Bottom - height));
                this.Width = width;
                this.Height = height;
                this.Left = left;
                this.Top = top;
                this.WindowStartupLocation = WindowStartupLocation.Manual;
            }
            catch { }
        }

        private void MainWindow_Closing(object sender, System.ComponentModel.CancelEventArgs e)
        {
            try
            {
                var dir = System.IO.Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "VioletToolBox");
                System.IO.Directory.CreateDirectory(dir);
                System.IO.File.WriteAllText(System.IO.Path.Combine(dir, "window_state.txt"),
                    "Left=" + this.Left + Environment.NewLine +
                    "Top=" + this.Top + Environment.NewLine +
                    "Width=" + this.Width + Environment.NewLine +
                    "Height=" + this.Height);
            }
            catch { }
        }

        private void SaveSidebarState()
        {
            try
            {
                var dir = System.IO.Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "VioletToolBox");
                System.IO.Directory.CreateDirectory(dir);
                var sb = new System.Text.StringBuilder();
                foreach (var kv in _groupExpanded)
                    sb.AppendLine(kv.Key + "=" + kv.Value);
                System.IO.File.WriteAllText(System.IO.Path.Combine(dir, "sidebar_state.txt"), sb.ToString());
            }
            catch { }
        }

        private void RestoreSidebarState()
        {
            try
            {
                var file = System.IO.Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "VioletToolBox", "sidebar_state.txt");
                if (!System.IO.File.Exists(file)) return;
                foreach (var ln in System.IO.File.ReadAllLines(file))
                {
                    var kv = ln.Split('=');
                    if (kv.Length != 2) continue;
                    if (bool.TryParse(kv[1], out var exp))
                        ToggleGroup(kv[0], exp);
                }
            }
            catch { }
        }

        private void ToggleGroup(string groupName, bool? expand = null)'''

if anchor not in c:
    print('ANCHOR NOT FOUND')
    sys.exit(1)
if 'private void RestoreWindowState()' in c:
    print('ALREADY INSERTED')
    sys.exit(0)
c = c.replace(anchor, methods, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(c)
print('methods inserted OK')
