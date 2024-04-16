#!/usr/bin/env python
# -*- coding: utf-8 -*-
from langchain_community.utilities.google_search import GoogleSearchAPIWrapper
from langchain_community.tools.google_search import GoogleSearchResults


class GoogleSearchTool(GoogleSearchResults):
    """
    Dependent environment variable:
        GOOGLE_API_KEY
        GOOGLE_CSE_ID
    """
    api_wrapper: GoogleSearchAPIWrapper = GoogleSearchAPIWrapper

    def _run(self, query: str, run_manager=None) -> str:
        return super()._run(query, run_manager)