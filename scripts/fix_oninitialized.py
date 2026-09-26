# -*- coding: utf-8 -*-
import io, sys
sys.stdout.reconfigure(encoding='utf-8')
fp = r'D:\doubao space\VioletToolBox\VioletToolBox\MainWindow.EdlFlash.cs'
t = io.open(fp, 'r', encoding='utf-8').read()
old = """        protected override void OnInitialized(EventArgs e)
        {
            base.OnInitialized(e);
            InitializeEdlEngine();
        }"""
new = """        protected override void OnInitialized(EventArgs e)
        {
            base.OnInitialized(e);
            CollectPageTemplateKeys();
            InitializeEdlEngine();
        }"""
assert old in t, 'OnInitialized anchor NOT FOUND'
t = t.replace(old, new, 1)
io.open(fp, 'w', encoding='utf-8', newline='').write(t)
print('OnInitialized collects template keys first')
