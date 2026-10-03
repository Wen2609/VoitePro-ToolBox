# -*- coding: utf-8 -*-
"""走本地转发代理推送"""
import subprocess, sys, os
sys.stdout.reconfigure(encoding='utf-8')

# 确保 git 走本地代理
subprocess.run(['git', 'config', '--global', 'http.proxy', 'http://127.0.0.1:7890'], capture_output=True)
subprocess.run(['git', 'config', '--global', 'https.proxy', 'http://127.0.0.1:7890'], capture_output=True)

env = dict(os.environ)
env['GIT_TERMINAL_PROMPT'] = '0'
r = subprocess.run(['git', 'push', 'origin', 'master'], capture_output=True, text=True, timeout=300, cwd=r'D:\doubao space\VioletToolBox', env=env)
with open(r'D:\doubao space\VioletToolBox\push_result.txt', 'w', encoding='utf-8') as out:
    out.write('exit=%d\nOUT:\n%s\nERR:\n%s\n' % (r.returncode, (r.stdout or '')[-1500:], (r.stderr or '')[-1500:]))
print('written, exit=', r.returncode)
