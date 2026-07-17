from __future__ import annotations

import argparse
import math
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote

import requests


def get_token() -> str:
    cmd = [
        "az",
        "account",
        "get-access-token",
        "--resource",
        "https://storage.azure.com/",
        "--query",
        "accessToken",
        "-o",
        "tsv",
    ]
    return subprocess.check_output(cmd, text=True).strip()


def request(method: str, url: str, token: str, **kwargs) -> requests.Response:
    headers = kwargs.pop("headers", {})
    headers.update(
        {
            "Authorization": f"Bearer {token}",
            "x-ms-version": "2023-11-03",
        }
    )
    response = requests.request(method, url, headers=headers, timeout=120, **kwargs)
    if not response.ok:
        raise RuntimeError(f"{method} {url} failed: {response.status_code} {response.text}")
    return response


def create_dir(base: str, path: str, token: str) -> None:
    url = f"{base}/{quote(path, safe='/')}?resource=directory"
    try:
        request("PUT", url, token)
    except RuntimeError as exc:
        if "PathAlreadyExists" not in str(exc) and "409" not in str(exc):
            raise


def upload_file(workspace: str, lakehouse: str, local_file: Path, remote_path: str, chunk_mb: int) -> str:
    token = get_token()
    workspace_q = quote(workspace, safe="")
    lakehouse_q = quote(f"{lakehouse}.Lakehouse", safe="")
    base = f"https://onelake.dfs.fabric.microsoft.com/{workspace_q}/{lakehouse_q}"
    remote_path = remote_path.strip("/")
    parent = "/".join(remote_path.split("/")[:-1])
    if parent:
        parts = parent.split("/")
        for i in range(1, len(parts) + 1):
            create_dir(base, "/".join(parts[:i]), token)

    file_url = f"{base}/{quote(remote_path, safe='/')}"
    request("PUT", f"{file_url}?resource=file", token)
    chunk = chunk_mb * 1024 * 1024
    total = local_file.stat().st_size
    offset = 0
    with local_file.open("rb") as fh:
        while True:
            data = fh.read(chunk)
            if not data:
                break
            request(
                "PATCH",
                f"{file_url}?action=append&position={offset}",
                token,
                data=data,
                headers={"Content-Type": "application/octet-stream"},
            )
            offset += len(data)
            print(f"uploaded {offset:,}/{total:,} bytes ({offset / total:.1%})")
    request("PATCH", f"{file_url}?action=flush&position={offset}", token)
    return file_url


def main() -> int:
    parser = argparse.ArgumentParser(description="Upload a local file to Microsoft Fabric OneLake Lakehouse Files.")
    parser.add_argument("--workspace", required=True, help="Fabric workspace display name, e.g. Apollis")
    parser.add_argument("--lakehouse", required=True, help="Lakehouse display name without .Lakehouse suffix")
    parser.add_argument("--local-file", required=True, type=Path)
    parser.add_argument("--remote-path", default="Files/Bronze/leatt_ecommerce_transactions_2m.parquet")
    parser.add_argument("--chunk-mb", type=int, default=8)
    args = parser.parse_args()

    if not args.local_file.exists():
        raise FileNotFoundError(args.local_file)
    url = upload_file(args.workspace, args.lakehouse, args.local_file, args.remote_path, args.chunk_mb)
    print(f"Upload complete: {url}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
