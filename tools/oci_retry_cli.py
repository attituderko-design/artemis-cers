import argparse
import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from urllib.request import Request, urlopen


RETRYABLE_KEYWORDS = (
    "Out of host capacity",
    "OutOfHostCapacity",
    "capacity",
    "Capacity",
    "TooManyRequests",
    "429",
)


def now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def post_webhook(url: str, text: str) -> None:
    if not url:
        return
    payload = json.dumps({"text": text}).encode("utf-8")
    req = Request(url, data=payload, headers={"Content-Type": "application/json"})
    try:
        urlopen(req, timeout=8).read()
    except Exception:
        pass


def launch_once(config_path: Path, region: str) -> tuple[bool, str, dict]:
    cmd = [
        "oci",
        "compute",
        "instance",
        "launch",
        "--from-json",
        f"file://{config_path.resolve()}",
        "--region",
        region,
    ]
    p = subprocess.run(cmd, capture_output=True, text=True)
    out = (p.stdout or "").strip()
    err = (p.stderr or "").strip()
    merged = f"{out}\n{err}".strip()

    if p.returncode == 0:
        try:
            obj = json.loads(out)
        except Exception:
            return False, f"JSON parse failed: {merged[:400]}", {}
        data = obj.get("data") if isinstance(obj, dict) else {}
        if isinstance(data, dict) and data.get("id", "").startswith("ocid1.instance"):
            return True, "ok", data
        return False, f"Launch command succeeded but instance id missing: {merged[:400]}", {}

    retryable = any(k in merged for k in RETRYABLE_KEYWORDS)
    if retryable:
        return False, f"retryable: {merged[:400]}", {}
    return False, f"fatal: {merged[:400]}", {}


def main() -> int:
    ap = argparse.ArgumentParser(description="OCI ARM instance launch retry tool (OCI CLI based)")
    ap.add_argument("--config", default="tools/launch_config.json", help="launch json path")
    ap.add_argument("--regions", default="ap-osaka-1", help="comma separated OCI regions")
    ap.add_argument("--interval", type=int, default=60, help="retry interval seconds")
    ap.add_argument("--max-retries", type=int, default=0, help="0 means infinite")
    ap.add_argument("--webhook", default="", help="optional webhook url for success/fatal")
    args = ap.parse_args()

    config_path = Path(args.config)
    if not config_path.exists():
        print(f"[{now()}] config not found: {config_path}")
        return 2

    regions = [r.strip() for r in args.regions.split(",") if r.strip()]
    if not regions:
        print(f"[{now()}] no regions provided")
        return 2

    try:
        cfg = load_json(config_path)
    except Exception as e:
        print(f"[{now()}] failed to read config: {e}")
        return 2

    display_name = cfg.get("displayName", "(no displayName)")
    print("=" * 60)
    print("ArtéMis OCI Retry (CLI)")
    print(f"Target: {display_name}")
    print(f"Regions: {', '.join(regions)}")
    print(f"Interval: {args.interval}s")
    print(f"Max retries: {'infinite' if args.max_retries == 0 else args.max_retries}")
    print("=" * 60)

    attempt = 0
    while True:
        attempt += 1
        print(f"\n[{now()}] Attempt {attempt}")
        for region in regions:
            print(f"  -> region={region}")
            ok, msg, data = launch_once(config_path, region)
            if ok:
                iid = data.get("id", "")
                ad = data.get("availability-domain", "")
                text = f"OCI launch success: {iid} ({region}, {ad})"
                print(f"[{now()}] SUCCESS {text}")
                post_webhook(args.webhook, text)
                return 0
            if msg.startswith("fatal:"):
                print(f"[{now()}] FATAL {msg}")
                post_webhook(args.webhook, f"OCI launch fatal: {msg}")
                return 1
            print(f"    retryable fail: {msg}")

        if args.max_retries > 0 and attempt >= args.max_retries:
            print(f"[{now()}] reached max retries: {args.max_retries}")
            return 1
        time.sleep(max(1, args.interval))


if __name__ == "__main__":
    sys.exit(main())

