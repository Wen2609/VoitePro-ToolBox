# -*- coding: utf-8 -*-
"""PrintWindow 截图：直接捕获指定 PID 窗口内部渲染，不受前台遮挡影响。
用法: python cap_printwin.py <pid> <out.png>
"""
import ctypes
import ctypes.wintypes as wt
import sys
from PIL import Image

user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32
PW_RENDERFULLCONTENT = 0x00000002


def find_proc_windows(pid):
    result = []

    @ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)
    def cb(hwnd, lparam):
        p = wt.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(p))
        if p.value == pid and user32.IsWindowVisible(hwnd):
            result.append(hwnd)
        return True

    user32.EnumWindows(cb, 0)
    return result


def main():
    pid = int(sys.argv[1])
    out = sys.argv[2]
    hwnds = find_proc_windows(pid)
    if not hwnds:
        print("NO WINDOW", file=sys.stderr)
        sys.exit(1)
    hwnd = hwnds[0]
    rect = wt.RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(rect))
    w = rect.right - rect.left
    h = rect.bottom - rect.top
    if w <= 0 or h <= 0:
        print("BAD RECT", rect, file=sys.stderr)
        sys.exit(1)

    hwnd_dc = user32.GetWindowDC(hwnd)
    mem_dc = gdi32.CreateCompatibleDC(hwnd_dc)
    bmp = gdi32.CreateCompatibleBitmap(hwnd_dc, w, h)
    old = gdi32.SelectObject(mem_dc, bmp)
    ok = user32.PrintWindow(hwnd, mem_dc, PW_RENDERFULLCONTENT)
    gdi32.SelectObject(mem_dc, old)

    # 从 HBITMAP 读像素
    class BITMAPINFOHEADER(ctypes.Structure):
        _fields_ = [
            ("biSize", wt.DWORD), ("biWidth", ctypes.c_long),
            ("biHeight", ctypes.c_long), ("biPlanes", wt.WORD),
            ("biBitCount", wt.WORD), ("biCompression", wt.DWORD),
            ("biSizeImage", wt.DWORD), ("biXPelsPerMeter", ctypes.c_long),
            ("biYPelsPerMeter", ctypes.c_long), ("biClrUsed", wt.DWORD),
            ("biClrImportant", wt.DWORD),
        ]

    bmi = BITMAPINFOHEADER()
    bmi.biSize = ctypes.sizeof(BITMAPINFOHEADER)
    bmi.biWidth = w
    bmi.biHeight = -h  # top-down
    bmi.biPlanes = 1
    bmi.biBitCount = 32
    bmi.biCompression = 0
    buf = ctypes.create_string_buffer(w * h * 4)
    got = gdi32.GetDIBits(mem_dc, bmp, 0, h, buf, ctypes.byref(bmi), 0)
    if not got:
        print("GetDIBits FAILED", file=sys.stderr)
        sys.exit(1)
    img = Image.frombytes("RGBA", (w, h), buf.raw)
    r, g, b, a = img.split()
    img = Image.merge("RGB", (b, g, r))  # BGRA -> RGB
    img.save(out)
    print(f"OK {w}x{h} printwindow={ok} -> {out}")

    gdi32.DeleteObject(bmp)
    gdi32.DeleteDC(mem_dc)
    user32.ReleaseDC(hwnd, hwnd_dc)


if __name__ == "__main__":
    main()
