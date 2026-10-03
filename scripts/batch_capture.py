# -*- coding: utf-8 -*-
"""批量截图：点击侧边栏各导航项并截图"""
import ctypes, time, subprocess, sys, os
sys.stdout.reconfigure(encoding='utf-8')

user32 = ctypes.windll.user32
WIN_X, WIN_Y = 455, 91  # 窗口左上角
def click(wx, wy):
    """窗口内像素坐标点击"""
    user32.SetCursorPos(WIN_X + wx, WIN_Y + wy)
    time.sleep(0.15)
    user32.mouse_event(0x0002, 0, 0, 0, 0)
    user32.mouse_event(0x0004, 0, 0, 0, 0)

ROOT = r'D:\doubao space\VioletToolBox'
PID = int(sys.argv[1]) if len(sys.argv) > 1 else 0
pages = [
    # (名称, 点击序列[(wx,wy)], 截图名)
    ('touping', [(34, 142)], 'ui_touping.png'),
    ('jibenshuru', [(66, 180), (42, 242)], 'ui_jibenshuru.png'),
    ('keshishuxie', [(66, 180), (42, 294)], 'ui_keshi.png'),
    ('oujiaxianshua', [(66, 180), (42, 346)], 'ui_oujia.png'),
    ('edl', [(66, 180), (42, 398)], 'ui_edl.png'),
    ('jiangji', [(66, 180), (42, 450)], 'ui_jiangji.png'),
    ('shiyong', [(66, 234)], 'ui_shiyong.png'),
    ('ziyuan', [(66, 288)], 'ui_ziyuan.png'),
    ('guanyu', [(34, 354)], 'ui_guanyu.png'),
]
# 展开刷写功能
click(66, 180)
time.sleep(0.8)
for name, clicks, shot in pages:
    # 若需要先回顶部（主页），点主页再重来
    for cx, cy in clicks:
        click(cx, cy)
        time.sleep(0.7)
    time.sleep(0.6)
    subprocess.run(['powershell', '-NoProfile', '-Command',
                    f'& "{ROOT}\\scripts\\cap_win2.ps1" -TargetPid {PID} -Out "{ROOT}\\{shot}"'],
                   capture_output=True, timeout=60)
    print(name, '->', shot)
