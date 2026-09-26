# -*- coding: utf-8 -*-
import ctypes, sys
sys.stdout.reconfigure(encoding='utf-8')
user32 = ctypes.windll.user32
pid = int(sys.argv[1]) if len(sys.argv) > 1 else 0
results = []
@ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
def cb(hwnd, lparam):
    p = ctypes.c_ulong()
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(p))
    if p.value == pid:
        length = user32.GetWindowTextLengthW(hwnd)
        buf = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buf, length + 1)
        cls = ctypes.create_unicode_buffer(256)
        user32.GetClassNameW(hwnd, cls, 256)
        visible = user32.IsWindowVisible(hwnd)
        results.append((hex(hwnd), buf.value[:40], cls.value, 'VIS' if visible else 'hid'))
    return True
user32.EnumWindows(cb, 0)
for r in results:
    print(r)
if not results:
    print('NO WINDOWS for pid', pid)
