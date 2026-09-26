# -*- coding: utf-8 -*-
import io, sys
sys.stdout.reconfigure(encoding='utf-8')
fp = r'D:\doubao space\VioletToolBox\VioletToolBox\MainWindow.EdlFlash.cs'
t = io.open(fp, 'r', encoding='utf-8').read()
old = """        protected override void OnInitialized(EventArgs e)
        {
            base.OnInitialized(e);
            CollectPageTemplateKeys();
            InitializeEdlEngine();
        }"""
new = """        protected override void OnInitialized(EventArgs e)
        {
            base.OnInitialized(e);
            CollectPageTemplateKeys();
            // 延迟 EDL 引擎初始化到窗口显示后，避免 WMI 端口枚举阻塞启动（懒加载下此初始化不依赖首帧）
            System.Windows.Application.Current?.Dispatcher.BeginInvoke(
                new System.Action(InitializeEdlEngine),
                System.Windows.Threading.DispatcherPriority.Background);
        }"""
assert old in t, 'OnInitialized anchor NOT FOUND'
t = t.replace(old, new, 1)
io.open(fp, 'w', encoding='utf-8', newline='').write(t)
print('InitializeEdlEngine deferred to Background priority')
