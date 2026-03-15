# OCI Retry Tool (CLI)

`tools/oci_retry_cli.py` launches an OCI instance with retry, using `oci` CLI auth/signing.

## 1) Prepare config

1. Copy `tools/launch_config.example.json` to `tools/launch_config.json`
2. Fill AD / compartment / image / subnet / ssh key

## 2) Run

```powershell
python tools/oci_retry_cli.py --config tools/launch_config.json --regions ap-osaka-1,ap-tokyo-1 --interval 60 --max-retries 0
```

- `--max-retries 0` means infinite retry
- Add `--webhook <url>` if you want success/fatal notifications

## Notes

- This avoids browser session signature expiry.
- Retryable errors are capacity-like errors; fatal auth/permission errors stop immediately.
