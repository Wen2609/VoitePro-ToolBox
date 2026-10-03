# -*- coding: utf-8 -*-
"""Alt技巧激活目标窗口后点击。用法: click_alt.py PID [x y ...]"""
import ctypes, time, sys
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

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

def activate():
    # 先恢复
    user32.ShowWindow(hwnd, 9)
    time.sleep(0.1)
    # Alt 技巧：按下 Alt 后 SetForegroundWindow 不再受限
    user32.keybd_event(0x12, 0, 0, 0)  # VK_MENU down
    time.sleep(0.05)
    user32.SetForegroundWindow(hwnd)
    time.sleep(0.05)
    user32.keybd_event(0x12, 0, 2, 0)  # VK_MENU up
    time.sleep(0.2)
    # 再试 BringWindowToTop
    user32.BringWindowToTop(hwnd)
    time.sleep(0.2)
    return user32.GetForegroundWindow() == hwnd

ok = activate()
print('activated:', ok, 'fg:', hex(user32.GetForegroundWindow()))

coords = [(int(sys.argv[i]), int(sys.argv[i+1])) for i in range(2, len(sys.argv), 2)]
for px, py in coords:
    if not ok:
        activate()
    user32.SetCursorPos(WIN_X + px, WIN_Y + py)
    time.sleep(0.2)
    user32.mouse_event(0x0002, 0, 0, 0, 0)
    user32.mouse_event(0x0004, 0, 0, 0, 0)
    time.sleep(0.8)
print('clicked', coords)
