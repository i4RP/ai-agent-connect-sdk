from __future__ import annotations


def merge_headers(*header_dicts: dict[str, str] | None) -> dict[str, str]:
    merged: dict[str, str] = {}
    for headers in header_dicts:
        if headers:
            merged.update(headers)
    return merged


def sanitize_url(url: str) -> str:
    url = url.rstrip("/")
    if not url.startswith(("http://", "https://")):
        url = f"https://{url}"
    return url


def truncate_string(s: str, max_length: int = 500) -> str:
    if len(s) <= max_length:
        return s
    return s[:max_length] + "..."
