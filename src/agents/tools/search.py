#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import List

from langchain_core.tools import BaseTool, tool

from agents.tools.base import SearchAPIAdapter
from documents import Query, Document


class SearchEngine(BaseTool):
    name: str = ''
    description: str = ''
    api_adapter: SearchAPIAdapter

    @classmethod
    def from_name(cls, name):
        _lookup_map = {}
        if name not in _lookup_map:
            raise KeyError(f'Supported SearchEngine: {[_lookup_map.keys()]}')
        api_adapter = _lookup_map[name]()
        return SearchEngine(api_adapter=api_adapter)

    def _run(self, query: str) -> List[Document]:
        return [Document(metadata=_meta) for _meta in self.api_adapter.run(query)]


@tool
def search_with_arxiv(query: str) -> List[Document]: ...


@tool
def search_with_wiki(query: str) -> List[Document]: ...


@tool
def generate_sub_query(query: str) -> List[Query]: ...
