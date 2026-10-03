# -*- coding: utf-8 -*-
"""通用点击：激活目标窗口后按窗口内像素坐标点击。用法: click_win.py PID x y [x2 y2 ...]"""
import ctypes, time, sys
user32 = ctypes.windll.user32

TARGET_PID = int(sys.argv[1])
WIN_X, WIN_Y = 455, 91

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

hwnd = find_hwnd(TARGET_PID)
if not hwnd:
    print('NO HWND')
    sys.exit(1)

def click(px, py):
    user32.SetForegroundWindow(hwnd)
    time.sleep(0.25)
    user32.SetCursorPos(WIN_X + px, WIN_Y + py)
    time.sleep(0.15)
    user32.mouse_event(0x0002, 0, 0, 0, 0)
    user32.mouse_event(0x0004, 0, 0, 0, 0)

coords = [(int(sys.argv[i]), int(sys.argv[i+1])) for i in range(2, len(sys.argv), 2)]
for px, py in coords:
    click(px, py)
    time.sleep(0.8)
print('clicked', coords)
