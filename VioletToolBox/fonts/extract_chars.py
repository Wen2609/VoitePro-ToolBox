# -*- coding: utf-8 -*-
"""Extract character set from VioletToolBox sources + GB2312 level-1 common chars."""
import os, re, sys

ROOT = r"D:\doubao space\VioletToolBox\VioletToolBox"
OUT = r"D:\doubao space\VioletToolBox\VioletToolBox\fonts\chars.txt"

cjk_re = re.compile(r'[\u3400-\u9FFF\uF900-\uFAFF]')
ascii_re = re.compile(r'[\u0020-\u007E\u00A0-\u00FF\u2010-\u2027\u2030-\u2049\u20AC\u3000-\u303F\uFF00-\uFFEF]')

chars = set()
count = 0

for dirpath, dirnames, filenames in os.walk(ROOT):
    # skip build output, git, bin, obj
    if any(x in dirpath for x in ('\\bin', '\\obj', '\\.git', '\\packages')):
        continue
    for fn in filenames:
        if not fn.endswith(('.xaml', '.cs')):
            continue
        p = os.path.join(dirpath, fn)
        try:
            with open(p, 'r', encoding='utf-8-sig', errors='ignore') as f:
                text = f.read()
        except Exception:
            continue
        count += 1
        for ch in text:
            if cjk_re.match(ch):
                chars.add(ch)
            elif ascii_re.match(ch):
                chars.add(ch)

# GB2312 level-1 hanzi: bytes 0xB0A1..0xD7F9 (3755 chars)
gbl1 = set()
for hi in range(0xB0, 0xD8):
    for lo in range(0xA1, 0xFF):
        try:
            ch = bytes([hi, lo]).decode('gb2312')
            gbl1.add(ch)
        except Exception:
            pass

all_chars = chars | gbl1
# sort: CJK first then ascii/punct for readability
def key(c):
    o = ord(c)
    if 0x3400 <= o <= 0x9FFF or 0xF900 <= o <= 0xFAFF:
        return (0, o)
    return (1, o)

sorted_chars = sorted(all_chars, key=key)
with open(OUT, 'w', encoding='utf-8') as f:
    f.write(''.join(sorted_chars))

print(f"scanned {count} files; source chars={len(chars)}; +GB2312-l1={len(gbl1 - chars)}; total={len(all_chars)}")
