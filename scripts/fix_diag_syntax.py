# -*- coding: utf-8 -*-
import io, sys, re
sys.stdout.reconfigure(encoding='utf-8')
fp = r'D:\doubao space\VioletToolBox\VioletToolBox\MainWindow.EdlFlash.cs'
t = io.open(fp, 'r', encoding='utf-8').read()
# 修复插桩语法：LogD("stepX") before <stmt> → LogD("stepX");\n<stmt>
t2 = re.sub(r'LogD\("(step[A-G])"\) before ', r'LogD("\1");\n            ', t)
# done 尾部：检查是否已加 done
if 'LogD("done")' not in t2:
    t2 = t2.replace('            InitializeEdlNativeLog();\n        }', '            InitializeEdlNativeLog();\n            LogD("done");\n        }', 1)
io.open(fp, 'w', encoding='utf-8', newline='').write(t2)
print('instrumentation syntax FIXED')
import subprocess
