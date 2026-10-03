# -*- coding: utf-8 -*-
"""批量截图 v3：千分比 -> 像素正确换算"""
import ctypes, time, subprocess, sys, os
sys.stdout.reconfigure(encoding='utf-8')

user32 = ctypes.windll.user32
WIN_X, WIN_Y = 455, 91
WIN_W, WIN_H = 1010, 850
TARGET_PID = int(sys.argv[1]) if len(sys.argv) > 1 else 0

def find_hwnd(pid):
    enum = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
    result = []
    def cb(hwnd, lparam):
        wpid = ctypes.c_ulong()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(wpid))
        if wpid.value == pid and user32.IsWindowVisible(hwnd):
            buf = ctypes.create_unicode_buffer(256)
            user32.GetWindowTextW(hwnd, buf, 256)
            if buf.value:
                result.append(hwnd)
        return True
    user32.EnumWindows(enum(cb), 0)
    return result[0] if result else None

HWND = find_hwnd(TARGET_PID)
if not HWND:
    print('NO HWND')
    sys.exit(1)

def click_r(x_perm, y_perm):
    """千分比坐标点击"""
    px = int(x_perm / 1000 * WIN_W)
    py = int(y_perm / 1000 * WIN_H)
    user32.SetForegroundWindow(HWND)
    time.sleep(0.2)
    user32.SetCursorPos(WIN_X + px, WIN_Y + py)
    time.sleep(0.15)
    user32.mouse_event(0x0002, 0, 0, 0, 0)
    user32.mouse_event(0x0004, 0, 0, 0, 0)

ROOT = r'D:\doubao space\VioletToolBox'
pages = [
    ('touping', [(34, 142)], 'ui_touping.png'),
    ('jibenshuru', [(42, 242)], 'ui_jibenshuru.png'),
    ('keshishuxie', [(42, 294)], 'ui_keshi.png'),
    ('oujia', [(42, 346)], 'ui_oujia.png'),
    ('edl', [(42, 398)], 'ui_edl.png'),
    ('jiangji', [(42, 450)], 'ui_jiangji.png'),
    ('shiyong', [(66, 234)], 'ui_shiyong.png'),
    ('ziyuan', [(66, 288)], 'ui_ziyuan.png'),
    ('guanyu', [(34, 354)], 'ui_guanyu.png'),
]
# 展开刷写功能
click_r(70, 190)
time.sleep(0.8)
for name, clicks, shot in pages:
    if name in ('jibenshuru', 'keshishuxie', 'oujia', 'edl', 'jiangji'):
        # 已在展开状态，直接点子项
        pass
    else:
        click_r(34, 86)  # 回主页
        time.sleep(0.5)
        click_r(70, 190)  # 展开
        time.sleep(0.5)
    for cx, cy in clicks:
        click_r(cx, cy)
        time.sleep(0.7)
    time.sleep(0.5)
    subprocess.run(['powershell', '-NoProfile', '-Command',
                    f'& "{ROOT}\\scripts\\cap_win2.ps1" -TargetPid {TARGET_PID} -Out "{ROOT}\\{shot}"'],
                   capture_output=True, timeout=60)
    print(name, shot, flush=True)
