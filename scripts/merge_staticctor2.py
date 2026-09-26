# -*- coding: utf-8 -*-
import io, re, sys
sys.stdout.reconfigure(encoding='utf-8')
csfp = r'D:\doubao space\VioletToolBox\VioletToolBox\MainWindow.xaml.cs'
t = io.open(csfp, 'r', encoding='utf-8').read()
pat = re.compile(r'        static MainWindow\(\)\n        \{\n(.*?)\n        \}\n\n', re.S)
blocks = pat.findall(t)
print('static ctor blocks found:', len(blocks))
if len(blocks) > 1:
    assigns = []
    for b in blocks:
        assigns.extend(re.findall(r'(_nameViewMapStatic\d+\["[^"]+"\] = "[^"]+";)', b))
    merged = '        static MainWindow()\n        {\n' + '\n'.join('            ' + a for a in assigns) + '\n        }\n\n'
    # 用索引替换：第一次出现的块换 merged，其余换空
    count = [0]
    def repl(m):
        count[0] += 1
        if count[0] == 1:
            return merged
        return ''
    t2 = pat.sub(repl, t)
    io.open(csfp, 'w', encoding='utf-8', newline='').write(t2)
    print('merged into single static ctor, assigns:', len(assigns))
else:
    print('no merge needed')
