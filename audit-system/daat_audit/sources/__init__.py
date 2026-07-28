# -*- coding: utf-8 -*-
"""Fournisseurs de textes sources (§15)."""
from .base import SourceDocument, TextSourceProvider
from .local import LocalProvider
from .sefaria import SefariaProvider

__all__ = ["SourceDocument", "TextSourceProvider", "LocalProvider", "SefariaProvider"]
