"""Starts FreshEggs on this computer and opens it in the default browser.

Used for the Windows .exe. Run with --lan to let phones on the same Wi-Fi connect
(needed by the Android app).
"""
import socket
import sys
import threading
import webbrowser

from app import app


def free_port(start=5000):
    for port in range(start, start + 20):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", port)) != 0:
                return port
    return start


def lan_address():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except OSError:
        return None


if __name__ == "__main__":
    lan = "--lan" in sys.argv
    port = free_port()
    host = "0.0.0.0" if lan else "127.0.0.1"
    print("=" * 56)
    print(" FreshEggs is running. Keep this window open.")
    print(f" On this computer:  http://127.0.0.1:{port}")
    if lan:
        print(f" From a phone:      http://{lan_address()}:{port}  (same Wi-Fi)")
    print(" Admin login:       http://127.0.0.1:%d/admin/login" % port)
    print(" Close this window to stop the app.")
    print("=" * 56)
    threading.Timer(1.2, lambda: webbrowser.open(f"http://127.0.0.1:{port}")).start()
    app.run(host=host, port=port, debug=False, use_reloader=False)
