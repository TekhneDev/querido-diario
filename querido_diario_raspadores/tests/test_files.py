import pytest
from scrapy.http import Response

from gazette.utils.files import detect_file_type

CLOUDFLARE_CHALLENGE_PAGE = (
    b"<!DOCTYPE html><html lang='en-US'><head><title>Just a moment...</title>"
    b'</head><body><div class="cf-turnstile"></div></body></html>'
)


def make_response(body, content_type=None):
    headers = {"Content-Type": content_type} if content_type else {}
    return Response("https://example.com/diario", body=body, headers=headers)


@pytest.mark.parametrize(
    "body, content_type, expected",
    [
        (b"%PDF-1.4 gazette", "application/pdf", "pdf"),
        (b"%PDF-1.7 gazette", None, "pdf"),
        # PDF header is allowed anywhere in the first 1024 bytes
        (b"\r\n\r\n%PDF-1.4 gazette", "application/octet-stream", "pdf"),
        # Content is trusted over a wrong Content-Type header
        (b"%PDF-1.4 gazette", "text/html", "pdf"),
        (b"PK\x03\x04" + b"\x00" * 300, "application/zip", "zip"),
        (b"{\\rtf1\\ansi gazette", None, "rtf"),
        (CLOUDFLARE_CHALLENGE_PAGE, "text/html; charset=UTF-8", "html"),
        (CLOUDFLARE_CHALLENGE_PAGE, "application/pdf", "html"),
        (b"\xef\xbb\xbf\n  <html><body>Prefeitura</body></html>", None, "html"),
        (b"<HEAD><TITLE>502 Proxy Error</TITLE></HEAD>", None, "html"),
        (
            b"<!-- Google tag (gtag.js) -->\n<script async src='x'></script>",
            None,
            "html",
        ),
        (b"Diario oficial em texto", "text/html", "html"),
        (b"Diario oficial em texto", "text/plain", "unknown"),
        (b"\x00\x01\x02\x03", "application/octet-stream", "unknown"),
    ],
)
def test_detect_file_type(body, content_type, expected):
    assert detect_file_type(make_response(body, content_type)) == expected
