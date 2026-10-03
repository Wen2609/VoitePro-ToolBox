# -*- coding: utf-8 -*-
"""本地 HTTPS CONNECT 转发代理：github.com -> 140.82.112.4，供 git push 绕过被墙 IP"""
import socket, threading, sys

HOST_MAP = {'github.com': '140.82.112.4', 'www.github.com': '140.82.112.4'}
LISTEN = ('127.0.0.1', 7890)
LOG = open(r'D:\doubao space\VioletToolBox\proxy_log.txt', 'a', encoding='utf-8', buffering=1)

def log(msg):
    LOG.write(msg + '\n')

def pipe(a, b):
    try:
        while True:
            d = a.recv(65536)
            if not d:
                break
            b.sendall(d)
    except Exception:
        pass
    finally:
        try:
            b.shutdown(socket.SHUT_WR)
        except Exception:
            pass

def handle_connect(client, target_host, target_port):
    host = HOST_MAP.get(target_host, target_host)
    log(f'CONNECT {target_host}:{target_port} -> {host}')
    try:
        up = socket.create_connection((host, target_port), timeout=25)
    except Exception as e:
        log(f'UPSTREAM FAIL {target_host}: {type(e).__name__}')
        try:
            client.sendall(b'HTTP/1.1 502 Bad Gateway\r\n\r\n')
        except Exception:
            pass
        client.close()
        return
    client.sendall(b'HTTP/1.1 200 Connection established\r\n\r\n')
    t1 = threading.Thread(target=pipe, args=(client, up), daemon=True)
    t2 = threading.Thread(target=pipe, args=(up, client), daemon=True)
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    client.close()
    up.close()
    log(f'CLOSED {target_host}')

def main():
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(LISTEN)
    srv.listen(50)
    log('proxy started on 127.0.0.1:7890')
    while True:
        try:
            c, _ = srv.accept()
            req = c.recv(4096).decode('latin1')
            line = req.splitlines()[0] if req else ''
            if line.startswith('CONNECT '):
                hostport = line.split(' ')[1]
                host, port = hostport.rsplit(':', 1)
                threading.Thread(target=handle_connect, args=(c, host, int(port)), daemon=True).start()
            else:
                c.close()
        except Exception:
            try:
                c.close()
            except Exception:
                pass

if __name__ == '__main__':
    main()
