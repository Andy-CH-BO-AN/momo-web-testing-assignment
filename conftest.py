import base64
from pathlib import Path
import re

import pytest
from pytest_html import extras

SCREENSHOT_DIR = Path("test-results/screenshots")


def _to_safe_filename(name: str) -> str:
    """Convert testcase name to a filesystem-safe filename."""
    cleaned = re.sub(r'[\\/:*?"<>|\s\[\]]+', "_", name)
    cleaned = re.sub(r"_+", "_", cleaned)
    return cleaned.strip("_")


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Capture a full-page failure screenshot before Playwright Page teardown and attach to HTML report."""
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        page = item.funcargs.get("page")
        if page is not None and not page.is_closed():
            try:
                screenshot_bytes = page.screenshot(full_page=True)

                safe_name = _to_safe_filename(item.name)
                SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
                screenshot_path = SCREENSHOT_DIR / f"{safe_name}.png"
                screenshot_path.write_bytes(screenshot_bytes)

                b64_content = base64.b64encode(screenshot_bytes).decode("utf-8")
                report_extras = getattr(report, "extras", [])
                report_extras.append(extras.png(b64_content, name="Failure Screenshot"))
                report.extras = report_extras
            except Exception:
                pass


@pytest.hookimpl(tryfirst=True)
def pytest_sessionfinish(session):
    """Ensure report directory exists before pytest-html writes the report."""
    htmlpath = session.config.getoption("htmlpath", None)
    if htmlpath:
        Path(htmlpath).parent.mkdir(parents=True, exist_ok=True)
