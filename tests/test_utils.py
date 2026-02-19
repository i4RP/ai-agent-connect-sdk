from ai_agent_sdk.utils.helpers import merge_headers, sanitize_url, truncate_string


def test_merge_headers_empty() -> None:
    assert merge_headers() == {}


def test_merge_headers_single() -> None:
    assert merge_headers({"A": "1"}) == {"A": "1"}


def test_merge_headers_multiple() -> None:
    result = merge_headers({"A": "1"}, {"B": "2"}, {"A": "3"})
    assert result == {"A": "3", "B": "2"}


def test_merge_headers_with_none() -> None:
    result = merge_headers({"A": "1"}, None, {"B": "2"})
    assert result == {"A": "1", "B": "2"}


def test_sanitize_url_strips_trailing_slash() -> None:
    assert sanitize_url("https://example.com/") == "https://example.com"


def test_sanitize_url_adds_https() -> None:
    assert sanitize_url("example.com") == "https://example.com"


def test_sanitize_url_preserves_http() -> None:
    assert sanitize_url("http://example.com") == "http://example.com"


def test_truncate_string_short() -> None:
    assert truncate_string("hello", 10) == "hello"


def test_truncate_string_exact() -> None:
    assert truncate_string("hello", 5) == "hello"


def test_truncate_string_long() -> None:
    result = truncate_string("hello world", 5)
    assert result == "hello..."
    assert len(result) == 8
