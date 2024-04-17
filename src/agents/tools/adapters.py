#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import List, TypedDict

from langchain_community.utilities.google_search import GoogleSearchAPIWrapper
from langchain_community.utilities.bing_search import BingSearchAPIWrapper
from langchain_community.utilities.duckduckgo_search import DuckDuckGoSearchAPIWrapper
from langchain_community.utilities.brave_search import BraveSearchWrapper
from langchain_community.utilities.searx_search import SearxSearchWrapper
from langchain_community.utilities.tavily_search import TavilySearchAPIWrapper


class SearchResult(TypedDict):
    title: str
    link: str
    summary: str


def search_adapter(cls, num_results, method='results', class_kwargs=None, **search_kwargs):
    instance = cls(**(class_kwargs or {}))

    def search(query):
        items = getattr(instance, method)(query, num_results, **search_kwargs)
        _results = []
        for item in items:
            _res = SearchResult(
                title=item.get('title'),
                link=item.get('link') or item.get('url'),
                summary=item.get('snippet') or item.get('description') or item.get('content')
            )
            assert _res['link']
            _results.append(_res)
        return _results
    return search


def get_search_fn(name: str, num_results: int):
    SEARCH_ENGINE_LOOKUP = {
        'google': search_adapter(GoogleSearchAPIWrapper, num_results),
        'bing': search_adapter(BingSearchAPIWrapper, num_results),
        'duckduckgo': search_adapter(DuckDuckGoSearchAPIWrapper, num_results),
        'tavily': search_adapter(TavilySearchAPIWrapper, num_results),
        'searx': search_adapter(SearxSearchWrapper, num_results),
        'brave': search_adapter(BraveSearchWrapper, num_results, '_search_request'),
    }
    if name not in SEARCH_ENGINE_LOOKUP:
        raise KeyError(f'Supported SearchEngine: {[SEARCH_ENGINE_LOOKUP.keys()]}')
    return SEARCH_ENGINE_LOOKUP[name]
