import datetime
import logging
import sys
import threading
import socket
import time
import os
from pathlib import Path
import webview
from bs4 import BeautifulSoup

def prune_old_logs(logs_dir: Path, max_files: int = 25):
    log_files = list(logs_dir.glob("log_*.log"))

    if len(log_files) <= max_files:
        return

    log_files.sort(key=lambda p: p.stat().st_mtime)
    to_delete = log_files[:-max_files]

    for old in to_delete:
        try:
            old.unlink()

        except Exception:
            pass

def setup_logging(base_dir: Path):
    logs_dir = base_dir / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)

    prune_old_logs(logs_dir, max_files=25)

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_filename = f"log_{timestamp}.log"
    log_path = logs_dir / log_filename
    log_file = open(log_path, "a", encoding="utf-8")

    sys.stdout = log_file
    sys.stderr = log_file

    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(log_path, encoding="utf-8"),
        ]
    )

    logging.info("=== New session log started: %s ===", timestamp)
    return log_file

def is_port_free(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex(("127.0.0.1", port)) != 0

def find_free_port(start: int = 8000, end: int = 8100) -> int:
    for port in range(start, end + 1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", port))
                return port

            except OSError:
                continue

    raise RuntimeError(f"No free port found in range {start}-{end}")

def run_fastapi(port: int):
    from app.main import app as fastapi_app
    import uvicorn
    uvicorn.run(fastapi_app, host="127.0.0.1", port=port, log_level="info")

def wait_for_server(port: int, timeout: float = 10.0) -> bool:
    start = time.time()

    while True:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=1):
                return True

        except Exception:
            if time.time() - start > timeout:
                return False
            time.sleep(0.5)

def get_title_from_index(static_dir: Path) -> str:
    index_path = static_dir / "index.html"

    if not index_path.exists():
        return "Assetto Companion"

    try:
        html = index_path.read_text(encoding="utf-8")
        soup = BeautifulSoup(html, "html.parser")
        title = soup.title.string if soup.title else "Assetto Companion"
        return title.strip()

    except Exception:
        return "Assetto Companion"

def main():
    if getattr(sys, "frozen", False):
        base_dir = Path(sys.executable).parent
        static_dir = Path(sys._MEIPASS) / "static"

    else:
        base_dir = Path(__file__).parent.resolve()
        static_dir = base_dir / "static"

    os.chdir(base_dir)

    log_file = setup_logging(base_dir)
    logging.info("Application starting; base_dir=%s", base_dir)

    try:
        port = find_free_port(8000, 8100)
    except Exception as e:
        logging.error("Failed to find free port: %s", e)
        return
    logging.info("Using port %d", port)

    server_thread = threading.Thread(target=run_fastapi, args=(port,), daemon=True)
    server_thread.start()

    if not wait_for_server(port, timeout=10.0):
        logging.error("FastAPI server did not start in time on port %d", port)
        return
    logging.info("FastAPI server is up on port %d", port)

    url = f"http://127.0.0.1:{port}/"
    logging.info("Opening WebView window at %s", url)

    title = get_title_from_index(static_dir)
    icon_path = static_dir / "img" / "icon.png"

    if not icon_path.exists():
        icon_path = None

    try:
        webview.create_window(title, url, width=1024, height=768,)
        webview.start()
        logging.info("WebView closed; exiting application.")

    except Exception as e:
        logging.exception("Error launching WebView: %s", e)


if __name__ == "__main__":
    main()