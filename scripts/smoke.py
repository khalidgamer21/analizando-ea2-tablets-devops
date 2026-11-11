"""Prueba HTTP local o remota de la publicación y del CSV desplegado."""

import argparse
import functools
import json
import threading
import time
import urllib.request
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


def verify(url: str, expected: int, commit: str | None = None) -> dict:
    started = time.perf_counter()
    with urllib.request.urlopen(url.rstrip("/") + "/health.json?check=" + str(time.time_ns()), timeout=25) as response:
        health = json.load(response)
    if health["status"] != "ok" or health["records"] != expected:
        raise ValueError("La publicación no contiene la cantidad esperada de registros.")
    if commit and health["commit"] != commit:
        raise ValueError("La publicación todavía no corresponde a la revisión esperada.")
    for resource in ["index.html", "catalogo_tablets.csv", "styles.css", "app.js"]:
        with urllib.request.urlopen(url.rstrip("/") + "/" + resource, timeout=25) as response:
            if response.status != 200 or not response.read():
                raise ValueError("Recurso vacío o inaccesible: " + resource)
    return {"status": "ok", "records": expected, "commit": health["commit"],
            "latency_ms": round((time.perf_counter() - started) * 1000, 2)}


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--directory", type=Path)
    group.add_argument("--url")
    parser.add_argument("--expected-records", type=int, default=80)
    parser.add_argument("--commit")
    parser.add_argument("--attempts", type=int, default=1)
    args = parser.parse_args()
    server = None
    if args.directory:
        handler = functools.partial(SimpleHTTPRequestHandler, directory=str(args.directory.resolve()))
        server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        url = f"http://127.0.0.1:{server.server_port}"
    else:
        url = args.url
    try:
        for attempt in range(args.attempts):
            try:
                print(json.dumps(verify(url, args.expected_records, args.commit), ensure_ascii=False))
                break
            except (OSError, ValueError):
                if attempt == args.attempts - 1:
                    raise
                time.sleep(4)
    finally:
        if server:
            server.shutdown()
            server.server_close()


if __name__ == "__main__":
    main()
