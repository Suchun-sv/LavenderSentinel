"""
pdf_extractor.py

使用 marker-pdf 将 PDF 转换为结构化 layout / markdown，并提供简单的 chunk 函数。

依赖：
    pip install marker-pdf pypdf

核心函数：
    - extract_pdf_layout(pdf_bytes: bytes) -> dict
    - extract_pdf_markdown(pdf_bytes: bytes) -> str
    - layout_to_chunks(layout: dict, max_chars: int = 1000) -> list[str]
"""

from __future__ import annotations

import io
import json
import tempfile
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List

from marker.config.parser import ConfigParser
from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.output import text_from_rendered
from pypdf import PdfReader


# ============ 基础工具 ============

def _is_probably_html(data: bytes) -> bool:
    """简单检查一下是不是被网站返回了 HTML（比如被 arXiv 的 reCAPTCHA 拦截）"""
    head = data[:200].lower()
    return b"<html" in head or b"<!doctype html" in head


@lru_cache(maxsize=1)
def get_marker_converter() -> PdfConverter:
    """
    懒加载全局 PdfConverter，避免每次都加载模型，非常耗时。

    注意：这里不传任何额外参数给 create_model_dict()，
    以兼容旧版本的 marker-pdf。
    """
    cfg = ConfigParser({}).generate_config_dict()
    model_dict = create_model_dict()
    return PdfConverter(model_dict, config=cfg)

def extract_pdf_markdown(pdf_bytes: bytes) -> str:
    """
    将 PDF（二进制）转换成 markdown 文本。

    返回示例：
    "# Title\n\n## Section 1\n\n...
    """
    if _is_probably_html(pdf_bytes):
        raise ValueError("Input looks like HTML, not a real PDF (maybe blocked by reCAPTCHA).")

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=True) as tmp:
        tmp.write(pdf_bytes)
        tmp.flush()

        converter = get_marker_converter()
        rendered = converter(tmp.name) 
        text_any, _, _ = text_from_rendered(rendered)
        return text_any

