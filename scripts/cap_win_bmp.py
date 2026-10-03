# -*- coding: utf-8 -*-
"""按 PID 截取主窗口截图"""
import ctypes, ctypes.wintypes as wt, sys, time
user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32

target = int(sys.argv[1])
outpath = sys.argv[2]

# 找主窗口（有标题、可见）
enum = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)
hwnd_found = []
def cb(hwnd, lparam):
    pid = wt.DWORD()
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    if pid.value == target:
        if user32.IsWindowVisible(hwnd):
            title = ctypes.create_unicode_buffer(256)
            user32.GetWindowTextW(hwnd, title, 256)
            if title.value:
                hwnd_found.append((hwnd, title.value))
    return True
user32.EnumWindows(enum(cb), 0)
if not hwnd_found:
    print('NO WINDOW')
    sys.exit(1)
# 取最大的窗口
hwnd, title = max(hwnd_found, key=lambda x: 0)
r = wt.RECT()
user32.GetWindowRect(hwnd, ctypes.byref(r))
w = r.right - r.left
h = r.bottom - r.top
print('win %s "%s" %dx%d' % (hex(hwnd), title, w, h))

# 截屏
hdc_win = user32.GetWindowDC(hwnd)
hdc_mem = gdi32.CreateCompatibleDC(hdc_win)
bmp = gdi32.CreateCompatibleBitmap(hdc_win, w, h)
gdi32.SelectObject(hdc_mem, bmp)
user32.PrintWindow(hwnd, hdc_mem, 2)  # PW_RENDERFULLCONTENT

class BITMAPINFOHEADER(wt.Structure):
    _fields_ = [('biSize', wt.DWORD), ('biWidth', wt.LONG), ('biHeight', wt.LONG),
                ('biPlanes', wt.WORD), ('biBitCount', wt.WORD), ('biCompression', wt.DWORD),
                ('biSizeImage', wt.DWORD), ('biXPelsPerMeter', wt.LONG), ('biYPelsPerMeter', wt.LONG),
                ('biClrUsed', wt.DWORD), ('biClrImportant', wt.DWORD)]
bih = BITMAPINFOHEADER()
bih.biSize = ctypes.sizeof(BITMAPINFOHEADER)
bih.biWidth = w
bih.biHeight = -h
bih.biPlanes = 1
bih.biBitCount = 32
bih.biCompression = 0
buf = ctypes.create_string_buffer(w * h * 4)
gdi32.GetDIBits(hdc_mem, bmp, 0, h, buf, ctypes.byref(bih), 0)

# BMP 文件
bmphdr = bytearray()
def w32(v): bmphdr.extend(v.to_bytes(4, 'little'))
def w16(v): bmphdr.extend(v.to_bytes(2, 'little'))
file_size = 14 + 40 + w * h * 4
bmphdr += b'BM'
w32(file_size); w32(0); w32(14 + 40)
w32(40); w32(w); w32(h); w16(1); w16(32); w32(0); w32(w*h*4); w32(0); w32(0); w32(0); w32(0)
# BGRA -> BGRX 已对齐
open(outpath + '.bmp', 'wb').write(bytes(bmphdr) + buf.raw)
print('saved', outpath + '.bmp')

gdi32.DeleteObject(bmp)
gdi32.DeleteDC(hdc_mem)
user32.ReleaseDC(hwnd, hdc_win)
