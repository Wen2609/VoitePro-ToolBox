# -*- coding: utf-8 -*-
"""PostMessage 注入鼠标消息到目标窗口。用法: click_post.py PID x y"""
import ctypes, time, sys
user32 = ctypes.windll.user32

WM_LBUTTONDOWN = 0x0201
WM_LBUTTONUP = 0x0202
MK_LBUTTON = 0x0001
TARGET_PID = int(sys.argv[1])

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

coords = [(int(sys.argv[i]), int(sys.argv[i+1])) for i in range(2, len(sys.argv), 2)]
for px, py in coords:
    lp = (py << 16) | (px & 0xFFFF)
    user32.PostMessageW(hwnd, WM_LBUTTONDOWN, MK_LBUTTON, lp)
    time.sleep(0.1)
    user32.PostMessageW(hwnd, WM_LBUTTONUP, 0, lp)
    time.sleep(0.6)
print('posted', coords)
