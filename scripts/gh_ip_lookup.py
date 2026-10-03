# -*- coding: utf-8 -*-
"""DoH 查询 github.com 真实 IP 并测试 443 连通"""
import json, sys, urllib.request, socket, time, ssl
sys.stdout.reconfigure(encoding='utf-8')
out = open(r'D:\doubao space\VioletToolBox\gh_ip_test.txt', 'w', encoding='utf-8')

def doh(name):
    for doh_url in ['https://dns.google/resolve?name=%s&type=A' % name,
                    'https://cloudflare-dns.com/dns-query?name=%s&type=A' % name]:
        try:
            req = urllib.request.Request(doh_url, headers={'accept': 'application/dns-json', 'User-Agent': 'Mozilla/5.0'})
            data = json.loads(urllib.request.urlopen(req, timeout=10).read())
            ips = [a['data'] for a in data.get('Answer', []) if a.get('type') == 1]
            if ips:
                return ips
        except Exception as e:
            out.write(f'doh {doh_url} err {type(e).__name__}\n')
    return []

ips = doh('github.com')
out.write(f'github.com A records: {ips}\n')
if not ips:
    # 回退：用 api.github.com 的 IP 段猜测不可靠，直接列常见
    ips = []

for ip in ips:
    t0 = time.time()
    try:
        s = socket.create_connection((ip, 443), timeout=5)
        out.write(f'DIRECT {ip}:443 OK ({time.time()-t0:.1f}s)\n')
        s.close()
    except Exception as e:
        out.write(f'DIRECT {ip}:443 FAIL {type(e).__name__}\n')

out.close()
