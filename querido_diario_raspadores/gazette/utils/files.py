import filetype

# Some spiders end up saving an HTML page (a portal home page, a document
# viewer, a blocking page, an error page...) instead of the gazette file.
# Nothing breaks during the crawl, but the data-processing step can't
# extract text from these files. Detecting the real file type allows us to
# measure and alert about it (see QueridoDiarioFilesPipeline and
# FileTypeMonitor).

# The PDF specification allows the "%PDF-" header to appear anywhere in the
# first 1024 bytes of the file
_PDF_HEADER_WINDOW = 1024
# filetype library only needs the first 261 bytes to guess most file types
_FILETYPE_HEADER_SIZE = 261

HTML_CONTENT_TYPES = (b"text/html", b"application/xhtml+xml")
HTML_START_MARKERS = (
    b"<!doctype html",
    b"<html",
    b"<head",
    b"<body",
    # HTML fragments (e.g. pages starting with an analytics snippet)
    b"<!--",
    b"<script",
)


def detect_file_type(response):
    """Return the type of the downloaded file based on its content.

    Returns the file extension when it is a known document type (e.g. "pdf",
    "zip", "rtf"), "html" when it is a web page and "unknown" otherwise.
    The content is checked before the Content-Type header, as websites
    sometimes send the wrong header.
    """
    body = response.body

    if b"%PDF-" in body[:_PDF_HEADER_WINDOW]:
        return "pdf"

    file_kind = filetype.guess(body[:_FILETYPE_HEADER_SIZE])
    if file_kind is not None:
        return file_kind.extension

    if _is_html(response):
        return "html"

    return "unknown"


def _is_html(response):
    content_type = response.headers.get("Content-Type", b"")
    mime_type = content_type.split(b";")[0].strip().lower()
    if mime_type in HTML_CONTENT_TYPES:
        return True

    beginning = response.body[:_PDF_HEADER_WINDOW].lstrip(b"\xef\xbb\xbf \t\r\n")
    return beginning.lower().startswith(HTML_START_MARKERS)
