# -*- coding: utf-8 -*-
import subprocess, time, ctypes, sys
sys.stdout.reconfigure(encoding='utf-8')
exe = r"D:\doubao space\VioletToolBox\VioletToolBox\bin\Debug\net8.0-windows\VioletToolBox.exe"
proc = subprocess.Popen([exe, "--page=OujiaFlashView"], cwd=__import__('os').path.dirname(exe))
print("pid", proc.pid)
for i in range(12):
    time.sleep(1)
    # 枚举该进程的窗口
    user32 = ctypes.windll.user32
    EnumWindows = user32.EnumWindows
    WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
    GetWindowThreadProcessId = user32.GetWindowThreadProcessId
    IsWindowVisible = user32.IsWindowVisible
    GetWindowRect = user32.GetWindowRect
    found = []
    @WNDENUMPROC
    def cb(h, l):
        pid = ctypes.c_ulong()
        GetWindowThreadProcessId(h, ctypes.byref(pid))
        if pid.value == proc.pid and IsWindowVisible(h):
            r = ctypes.wintypes.RECT()
            GetWindowRect(h, ctypes.byref(r))
            w = r.right - r.left; hh = r.bottom - r.top
            found.append((w, hh))
        return True
    EnumWindows(cb, 0)
    print(f"t={i+1}s windows={found} poll={proc.poll()}")
proc.kill()
print("killed")
