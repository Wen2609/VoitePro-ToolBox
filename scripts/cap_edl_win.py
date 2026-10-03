# -*- coding: utf-8 -*-
"""Win32 PrintWindow 截图 VioletToolBox 窗口"""
import ctypes, ctypes.wintypes as wt, sys
sys.stdout.reconfigure(encoding='utf-8')

user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32

pid = 12192
hwnd = ctypes.c_void_p()

EnumProc = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)
def enum_proc(h, l):
    global hwnd
    p = wt.DWORD()
    user32.GetWindowThreadProcessId(h, ctypes.byref(p))
    if p.value == pid and user32.IsWindowVisible(h):
        hwnd = h
        return False
    return True
user32.EnumWindows(EnumProc(enum_proc), 0)
if not hwnd:
    print('WINDOW NOT FOUND')
    sys.exit(1)

print('hwnd =', hex(hwnd.value))
rect = wt.RECT()
user32.GetWindowRect(hwnd, ctypes.byref(rect))
w = rect.right - rect.left
h = rect.bottom - rect.top
print(f'rect: ({rect.left},{rect.top}) {w}x{h}')

# 截图
hdc = user32.GetWindowDC(hwnd)
memdc = gdi32.CreateCompatibleDC(hdc)
bmp = gdi32.CreateCompatibleBitmap(hdc, w, h)
old = gdi32.SelectObject(memdc, bmp)
user32.PrintWindow(hwnd, memdc, 2)  # PW_RENDERFULLCONTENT

class BITMAPINFOHEADER(ctypes.Structure):
    _fields_ = [
        ('biSize', wt.DWORD), ('biWidth', wt.LONG), ('biHeight', wt.LONG),
        ('biPlanes', wt.WORD), ('biBitCount', wt.WORD), ('biCompression', wt.DWORD),
        ('biSizeImage', wt.DWORD), ('biXPelsPerMeter', wt.LONG), ('biYPelsPerMeter', wt.LONG),
        ('biClrUsed', wt.DWORD), ('biClrImportant', wt.DWORD),
    ]

bih = BITMAPINFOHEADER()
bih.biSize = ctypes.sizeof(BITMAPINFOHEADER)
bih.biWidth = w
bih.biHeight = -h
bih.biPlanes = 1
bih.biBitCount = 32
bih.biCompression = 0

buf = ctypes.create_string_buffer(w * h * 4)
gdi32.GetDIBits(memdc, bmp, 0, h, buf, ctypes.byref(bih), 0)

gdi32.SelectObject(memdc, old)
gdi32.DeleteDC(memdc)
user32.ReleaseDC(hwnd, hdc)
gdi32.DeleteObject(bmp)

# 保存 BMP
out = r'D:\doubao space\VioletToolBox\edl_win_cap.bmp'
with open(out, 'wb') as f:
    # 简单 BMP 头（BITMAPFILEHEADER）
    row = w * 4
    pad = (4 - (row % 4)) % 4
    row_stride = row + pad
    pixel_size = row_stride * h
    file_size = 14 + 40 + pixel_size
    f.write(b'BM')
    f.write(ctypes.c_uint32(file_size))
    f.write(ctypes.c_uint16(0))
    f.write(ctypes.c_uint16(0))
    f.write(ctypes.c_uint32(54))
    f.write(bytes(bytearray(bih)))  # 40 bytes header
    # 像素（BGRA→BGR，补 pad）
    data = bytearray(buf.raw)
    for y in range(h):
        row_start = y * w * 4
        f.write(data[row_start:row_start + w * 4][0::4])  # 每 4 字节取前 3（BGR）——错误，逐字节
print('saved', out, 'size', file_size)
