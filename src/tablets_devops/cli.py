"""Comandos reproducibles del proyecto."""

import argparse
import json
from pathlib import Path

from tablets_devops.data import replay_snapshot, save_csv, validate_dataset
from tablets_devops.site import build_site


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Catálogo de tablets con BeautifulSoup y DevOps")
    parser.add_argument("command", choices=["build", "replay"])
    parser.add_argument("--snapshot", type=Path, default=Path("data/snapshot"))
    parser.add_argument("--output", type=Path)
    parser.add_argument("--commit", default="local")
    parser.add_argument("--run-url", default="")
    args = parser.parse_args(argv)
    frame, _ = replay_snapshot(args.snapshot)
    quality = validate_dataset(frame, minimum_rows=50)
    if args.command == "build":
        destination = args.output or Path("build/site")
        result = build_site(frame, destination, args.commit, args.run_url)
    else:
        destination = args.output or Path("build/catalogo_tablets.csv")
        save_csv(frame, destination)
        result = quality
    print(json.dumps({"event": args.command, "output": str(destination), "result": result}, ensure_ascii=False))
    return 0
