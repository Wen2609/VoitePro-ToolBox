# -*- coding: utf-8 -*-
import io, sys
sys.stdout.reconfigure(encoding='utf-8')
fp = r'D:\doubao space\VioletToolBox\VioletToolBox\MainWindow.EdlFlash.cs'
t = io.open(fp, 'r', encoding='utf-8').read()
old = """        private void LoadEdlPorts()
        {
            if ((this.FindControlInPages("EdlPortComboBox") as System.Windows.Controls.ComboBox) == null)
                return;
            (this.FindControlInPages("EdlPortComboBox") as System.Windows.Controls.ComboBox).ItemsSource = BuildEdlPortOptions();
        }"""
new = """        private void LoadEdlPorts()
        {
            var cb = this.FindControlInPages("EdlPortComboBox") as System.Windows.Controls.ComboBox;
            if (cb == null) return;
            var ui = this.Dispatcher;
            // WMI 端口枚举可能在 UI 线程阻塞数秒，移到后台线程，结果回 UI
            System.Threading.Tasks.Task.Run(() => BuildEdlPortOptions()).ContinueWith(antecedent =>
            {
                ui.Invoke(new System.Action(() =>
                {
                    var c = this.FindControlInPages("EdlPortComboBox") as System.Windows.Controls.ComboBox;
                    if (c != null && antecedent.IsCompletedSuccessfully)
                        c.ItemsSource = antecedent.Result;
                }));
            });
        }"""
assert old in t, 'LoadEdlPorts anchor NOT FOUND'
t = t.replace(old, new, 1)
io.open(fp, 'w', encoding='utf-8', newline='').write(t)
print('LoadEdlPorts async (WMI off UI thread)')
