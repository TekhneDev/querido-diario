from scrapy import Spider
from scrapy.utils.test import get_crawler
from spidermon import MonitorSuite
from spidermon.contrib.scrapy.runners import SpiderMonitorRunner

from gazette import monitors


class FileTypeMonitorSuite(MonitorSuite):
    monitors = [monitors.FileTypeMonitor]


def run_file_type_monitor(stats, settings=None):
    crawler = get_crawler(Spider, settings_dict=settings or {})
    spider = Spider(name="test")
    runner = SpiderMonitorRunner(spider=spider)
    result = runner.run(
        FileTypeMonitorSuite(),
        stats=stats,
        crawler=crawler,
        spider=spider,
        stats_history=[],
        job=None,
    )
    [monitor_result] = result.monitor_results
    return monitor_result


def test_file_type_monitor_passes_when_only_documents_are_downloaded():
    result = run_file_type_monitor({"file_type/pdf": 10, "file_type/zip": 1})
    assert result.status == "OK"


def test_file_type_monitor_fails_when_html_pages_are_downloaded():
    result = run_file_type_monitor({"file_type/pdf": 9, "file_type/html": 1})
    assert result.status == "FAIL"
    assert "1 of 10 downloaded files are HTML pages" in result.reason


def test_file_type_monitor_respects_configured_ratio():
    stats = {"file_type/pdf": 9, "file_type/html": 1}
    settings = {"QUERIDODIARIO_MAX_HTML_FILES_RATIO": 0.1}
    assert run_file_type_monitor(stats, settings).status == "OK"


def test_file_type_monitor_can_be_disabled():
    stats = {"file_type/html": 5}
    settings = {"QUERIDODIARIO_MAX_HTML_FILES_RATIO": 1}
    assert run_file_type_monitor(stats, settings).status == "OK"


def test_file_type_monitor_is_skipped_without_downloaded_files():
    result = run_file_type_monitor({"item_scraped_count": 0})
    assert result.status == "SKIPPED"
