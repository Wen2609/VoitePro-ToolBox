# -*- coding: utf-8 -*-
"""诊断：鼠标点位置窗口、前台窗口、目标窗口关系"""
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
fg = user32.GetForegroundWindow()
print('target hwnd:', hex(hwnd))
print('foreground  :', hex(fg))

def title_of(h):
    buf = ctypes.create_unicode_buffer(256)
    user32.GetWindowTextW(h, buf, 256)
    pid = ctypes.c_ulong()
    user32.GetWindowThreadProcessId(h, ctypes.byref(pid))
    return '[%s pid=%d]' % (buf.value, pid.value)

print('fg title:', title_of(fg))

# 鼠标位置窗口
sx, sy = WIN_X + 98, WIN_Y + 165
user32.SetCursorPos(sx, sy)
time.sleep(0.3)
pt = ctypes.wintypes.POINT()
ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
wfp = user32.WindowFromPoint(pt)
print('point (%d,%d) -> window:' % (pt.x, pt.y), hex(wfp), title_of(wfp))
print('wfp is target:', wfp == hwnd)

# 激活后再次检查
user32.ShowWindow(hwnd, 9)
user32.SetForegroundWindow(hwnd)
time.sleep(0.5)
print('fg after activate:', hex(user32.GetForegroundWindow()))
