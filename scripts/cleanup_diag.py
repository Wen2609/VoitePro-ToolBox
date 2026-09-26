# -*- coding: utf-8 -*-
import io, re, sys
sys.stdout.reconfigure(encoding='utf-8')

# 1) 清理 MainWindow.EdlFlash.cs 诊断
fp = r'D:\doubao space\VioletToolBox\VioletToolBox\MainWindow.EdlFlash.cs'
t = io.open(fp, 'r', encoding='utf-8').read()

# 恢复 OnInitialized（去掉诊断块）
old_oni = """        protected override void OnInitialized(EventArgs e)
        {
            base.OnInitialized(e);
            var _swDiag = System.Diagnostics.Stopwatch.StartNew();
            try
            {
                var dbg = new System.Text.StringBuilder();
                dbg.AppendLine("OnInitialized " + System.DateTime.Now.ToString("HH:mm:ss.fff"));
                dbg.AppendLine("resKeys=" + this.Resources.Count);
                foreach (var k in this.Resources.Keys) dbg.AppendLine("K=" + k);
                var dt = this.FindResource("Page_EdlFlashView") as System.Windows.DataTemplate;
                dbg.AppendLine("dt=" + (dt != null ? "FOUND" : "NULL"));
                if (dt != null) { var o = dt.LoadContent(); dbg.AppendLine("load=" + (o != null ? o.GetType().Name : "NULL")); }
                dbg.AppendLine("diagPreInitMs=" + _swDiag.ElapsedMilliseconds);
                System.IO.File.WriteAllText(System.IO.Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "dbg_oni.log"), dbg.ToString());
            }
            catch (Exception ex) { System.IO.File.WriteAllText(System.IO.Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "dbg_oni.log"), "EX " + ex); }
            CollectPageTemplateKeys();
            InitializeEdlEngine();
            System.IO.File.AppendAllText(System.IO.Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "dbg_oni.log"), "EdlEngineInitMs=" + _swDiag.ElapsedMilliseconds + "\\r\\n");
        }"""
new_oni = """        protected override void OnInitialized(EventArgs e)
        {
            base.OnInitialized(e);
            CollectPageTemplateKeys();
            InitializeEdlEngine();
        }"""
if old_oni in t:
    t = t.replace(old_oni, new_oni, 1)
    print('OnInitialized diagnostic removed')
else:
    print('OnInitialized pattern NOT FOUND (may differ)')

# 恢复 InitializeEdlEngine（去掉 LogD 插桩）
# 用正则把 LogD(...); 行删除，把 "LogD("stepX");\n            " 前缀删
t2 = re.sub(r'            LogD\("[^"]+"\);\n', '', t)
# 删 _swE 和 LogD 定义
t2 = re.sub(r'            var _swE = System\.Diagnostics\.Stopwatch\.StartNew\(\);\n            string LogD\(string m\) \{ try \{ System\.IO\.File\.AppendAllText\(System\.IO\.Path\.Combine\(AppDomain\.CurrentDomain\.BaseDirectory, "dbg_edl\.log"\), m \+ " ms=" \+ _swE\.ElapsedMilliseconds \+ "\\r\\n"\); \} catch \{ \} return m; \}\n', '', t2)
# 删 dbg 诊断块（L221 前的 try/catch）
t2 = re.sub(r'            try\n            \{\n                var _sv = StaticNameView\("EdlPartitionDataGrid"\);\n.*?\n            \}\n            catch \(Exception _ex\) \{ LogD\("dbg EX " \+ _ex\.Message\); \}\n', '', t2, flags=re.S)
if 'LogD(' in t2:
    print('WARNING: remaining LogD:', len(re.findall(r'LogD\(', t2)))
io.open(fp, 'w', encoding='utf-8', newline='').write(t2)
print('EdlFlash diagnostics cleaned')

# 2) 删除诊断日志文件
import os
for f in ['dbg_oni.log', 'dbg_edl.log']:
    p = os.path.join(r'D:\doubao space\VioletToolBox\VioletToolBox\bin\Debug\net8.0-windows', f)
    if os.path.exists(p):
        os.remove(p)
        print('removed', f)

# 3) 删除 xl 测试项目
import shutil
xl = r'D:\doubao space\VioletToolBox\xl'
if os.path.exists(xl):
    shutil.rmtree(xl, ignore_errors=True)
    print('removed xl test project')
