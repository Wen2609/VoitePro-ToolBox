# -*- coding: utf-8 -*-
import ctypes, ctypes.wintypes as wt, sys
user32 = ctypes.windll.user32
target = int(sys.argv[1]) if len(sys.argv) > 1 else -1
enum = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)
found = []
def cb(hwnd, lparam):
    pid = wt.DWORD()
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    if pid.value == target:
        title = ctypes.create_unicode_buffer(512)
        user32.GetWindowTextW(hwnd, title, 512)
        if title.value:
            r = wt.RECT()
            user32.GetWindowRect(hwnd, ctypes.byref(r))
            found.append('%s "%s" rect=%d,%d,%d,%d' % (hex(hwnd), title.value, r.left, r.top, r.right, r.bottom))
    return True
user32.EnumWindows(enum(cb), 0)
open(r'D:\doubao space\VioletToolBox\win_enum.txt', 'w', encoding='utf-8').write('\n'.join(found))
print('windows:', len(found))
