# -*- coding: utf-8 -*-
"""SendInput 注入真实鼠标点击。用法: click_si.py sx sy"""
import ctypes, time, sys
user32 = ctypes.windll.user32

INPUT_MOUSE = 0
MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_ABSOLUTE = 0x8000
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004

class MOUSEINPUT(ctypes.Structure):
    _fields_ = [('dx', ctypes.c_long), ('dy', ctypes.c_long),
                ('mouseData', ctypes.c_ulong), ('dwFlags', ctypes.c_ulong),
                ('time', ctypes.c_ulong), ('dwExtraInfo', ctypes.POINTER(ctypes.c_ulong))]
class INPUT(ctypes.Structure):
    _fields_ = [('type', ctypes.c_ulong), ('mi', MOUSEINPUT)]

def mouse_abs(x, y, flags):
    inp = INPUT()
    inp.type = INPUT_MOUSE
    inp.mi = MOUSEINPUT(int(x), int(y), 0, flags, 0, None)
    return inp

# 屏幕尺寸
sw = user32.GetSystemMetrics(0)
sh = user32.GetSystemMetrics(1)

sx, sy = int(sys.argv[1]), int(sys.argv[2])
# 归一化到 0-65535
ax = int(sx * 65535 / sw)
ay = int(sy * 65535 / sh)

# 先移动
move = (INPUT * 1)(mouse_abs(ax, ay, MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE))
user32.SendInput(1, move, ctypes.sizeof(INPUT))
time.sleep(0.2)

# 按下+抬起（一次发送）
click = (INPUT * 2)(
    mouse_abs(ax, ay, MOUSEEVENTF_LEFTDOWN),
    mouse_abs(ax, ay, MOUSEEVENTF_LEFTUP)
)
user32.SendInput(2, click, ctypes.sizeof(INPUT))
print('sent', sx, sy)
