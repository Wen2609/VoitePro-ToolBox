# -*- coding: utf-8 -*-
import io, re, sys
sys.stdout.reconfigure(encoding='utf-8')
body = io.open(r'D:\doubao space\VioletToolBox\autoroot_body.txt', 'r', encoding='utf-8').read()
out = []
# 找所有 ControlTemplate 内容
for m in re.finditer(r'<ControlTemplate[^>]*>(.*?)</ControlTemplate>', body, re.S):
    tpl = m.group(1)
    out.append('TPL ctx: %s' % tpl.replace('\n', ' ')[:400])
    out.append('  len=%d buttons=%d styles=%d refs=%s' % (
        len(tpl),
        len(re.findall(r'<Button', tpl)),
        len(re.findall(r'<Style', tpl)),
        re.findall(r'\{StaticResource ([^}]+)\}', tpl)[:5]))
    # 找嵌套 Button 模板内
    for bm in re.finditer(r'<Button[^>]*>', tpl):
        out.append('  BUTTON: %s' % bm.group(0)[:150])
io.open(r'D:\doubao space\VioletToolBox\autoroot_tpl.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('templates:', len(re.findall(r'<ControlTemplate', body)))
