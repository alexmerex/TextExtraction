from dataclasses import replace

import pytest

from text_extraction.config import PipelineConfig
from text_extraction.downloader import DownloadError, ensure_minie_jar


def test_download_rejects_non_http_urls(config: PipelineConfig) -> None:
    configured = replace(config, minie_url="file:///tmp/minie.jar")

    with pytest.raises(DownloadError, match="http or https"):
        ensure_minie_jar(configured)
