#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pathlib import Path

SEARCHER_PROMPT = (
    'You are a search assistant that helps users search for Internet resources'
    'You are researching topics about "{topic}" through various resources'
    "I'm going to give you some problems that you have to use tools to deal with"
)
READER_PROMPT = (
    'You are a text analysis assistant that helps users discover valuable information'
    'You are researching topics about "{topic}" through various resources'
    "I'm going to give you some information from Internet that you have to use tools to deal with"
)
DEFAULT_SEARCH_ENGINE = 'duckduckgo'
PAGE_CONTENT_KEYS = ['summary', 'title', 'keywords', 'content']
MAX_CHUNK_SIZE = 4000
NUM_RESULTS = 5
DATA_DIR = Path('./')