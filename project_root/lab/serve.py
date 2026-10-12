

import argparse
import functools
import os
import sys
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from typing import List, Optional, Tuple

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from lab.errors import LabError 
from lab.publish import publish 


class Hub:
    """Счётчик изменений: слушатель увеличивает, открытые страницы ждут."""

    def __init__(self) -> None:
        self.counter = 0
        self._cond = threading.Condition()

    def notify(self) -> None:
        with self._cond:
            self.counter += 1
            self._cond.notify_all()

    def wait(self, last: int, timeout: float) -> int:
        with self._cond:
            self._cond.wait_for(lambda: self.counter != last, timeout)
            return self.counter


class Watcher(threading.Thread):
    """Фоновый слушатель: опрашивает CSV и при изменении обновляет data.json."""

    def __init__(self, csv_path: str, out_path: str, hub: Hub, interval: float = 1.0) -> None:
        super().__init__(daemon=True)
        self.csv_path, self.out_path = csv_path, out_path
        self.hub, self.interval = hub, interval
        self._signature: Optional[Tuple[int, int]] = None
        self._stop_event = threading.Event()

    def _stat(self) -> Optional[Tuple[int, int]]:
        try:
            st = os.stat(self.csv_path)
            return (st.st_mtime_ns, st.st_size)
        except OSError:
            return None

    def check(self) -> bool:
        """Одна проверка. True - data.json обновлён и страницы уведомлены."""
        sig = self._stat()
        if sig is None or sig == self._signature:
            return False
        try:
            changed = publish(self.csv_path, self.out_path)
        except LabError as exc: 
            print(f"[слушатель] файл пока не прочитан: {exc}")
            return False
        self._signature = sig
        if changed:
            print("[слушатель] CSV изменился -> data.json обновлён")
            self.hub.notify()
        return changed

    def run(self) -> None:
        while True:
            self.check()
            if self._stop_event.wait(self.interval):
                return

    def stop(self) -> None:
        self._stop_event.set()


class Handler(SimpleHTTPRequestHandler):
    """Раздаёт папку site/ (только чтение) и поток событий /events."""

    hub: Hub = Hub()

    def log_message(self, fmt: str, *args: object) -> None:
        pass

    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-cache")
        super().end_headers()

    def do_GET(self) -> None:
        if self.path.split("?")[0] == "/events":
            self._events()
        else:
            super().do_GET()

    def _events(self) -> None:
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.end_headers()
        last = self.hub.counter
        try:
            self.wfile.write(b"retry: 3000\n\n")
            self.wfile.flush()
            while True:
                current = self.hub.wait(last, 15)
                if current != last:
                    last = current
                    self.wfile.write(b"data: update\n\n")
                else:
                    self.wfile.write(b": ping\n\n")
                self.wfile.flush()
        except OSError: 
            return

    def _deny(self) -> None:
        self.send_error(405, "Read-only", "Сайт доступен только для просмотра")

    do_POST = do_PUT = do_DELETE = do_PATCH = _deny


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Сайт (только просмотр) + слушатель CSV")
    parser.add_argument("--csv", default=os.path.join(_PROJECT_ROOT, "data", "students.csv"))
    parser.add_argument("--out", default=os.path.join(_PROJECT_ROOT, "site", "data.json"))
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--interval", type=float, default=1.0, help="период проверки CSV, сек")
    args = parser.parse_args(argv)

    hub = Handler.hub
    watcher = Watcher(args.csv, args.out, hub, args.interval)
    watcher.check() 
    watcher.start()

    handler = functools.partial(Handler, directory=os.path.dirname(os.path.abspath(args.out)))
    try:
        server = ThreadingHTTPServer(("127.0.0.1", args.port), handler)
    except OSError as exc:
        print(f"Не удалось занять порт {args.port}: {exc}. Попробуйте --port 8080")
        return 1
    print(f"Сайт: http://127.0.0.1:{args.port}/   слушатель: {args.csv}   (стоп: Ctrl+C)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nОстановлено.")
    finally:
        watcher.stop()
        server.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
