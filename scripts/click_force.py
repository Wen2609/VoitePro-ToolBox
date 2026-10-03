# -*- coding: utf-8 -*-
"""诊断+强点：检查前台窗口，激活后 SendInput 点击"""
import ctypes, time, sys
user32 = ctypes.windll.user32

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

fg = user32.GetForegroundWindow()
print('foreground:', hex(fg), 'target:', hex(hwnd), 'same:', fg == hwnd)

# 强制激活（多种方式）
user32.ShowWindow(hwnd, 9)  # SW_RESTORE
user32.SetForegroundWindow(hwnd)
time.sleep(0.3)
# 附加线程输入以便 SetForegroundWindow 生效
fg_thread = user32.GetWindowThreadProcessId(fg, None)
target_thread = user32.GetWindowThreadProcessId(hwnd, None)
if fg_thread != target_thread:
    user32.AttachThreadInput(target_thread, fg_thread, True)
    user32.SetForegroundWindow(hwnd)
    user32.BringWindowToTop(hwnd)
    time.sleep(0.3)
    user32.AttachThreadInput(target_thread, fg_thread, False)
user32.SetForegroundWindow(hwnd)
time.sleep(0.5)
print('after activate fg:', hex(user32.GetForegroundWindow()))

WIN_X, WIN_Y = 455, 91
# 点击"刷写功能" 窗口内(98,165)
px, py = 98, 165
user32.SetCursorPos(WIN_X + px, WIN_Y + py)
time.sleep(0.2)
user32.mouse_event(0x0002, 0, 0, 0, 0)
user32.mouse_event(0x0004, 0, 0, 0, 0)
time.sleep(1.0)
print('clicked at', WIN_X + px, WIN_Y + py)
