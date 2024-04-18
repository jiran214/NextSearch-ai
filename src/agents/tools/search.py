#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from typing import List, Literal, Callable
from arxiv import Result
from langchain_core.tools import BaseTool, tool
from wikipedia import WikipediaPage

from agents.tools.adapters import get_search_fn, SearchResult
from langchain_community.utilities.arxiv import ArxivAPIWrapper
from langchain_community.utilities.wikipedia import WikipediaAPIWrapper
from agents.tools.parsers import collect_url_content, collect_pdf
from documents import Query, Document, Metadata

arxiv_wrapper = ArxivAPIWrapper()
wiki_wrapper = WikipediaAPIWrapper()


logger = logging.getLogger(__name__)


class SearchEngine(BaseTool):
    name: str = 'search_engine'
    description: str = (
        "A wrapper around Google Search. "
        "Useful for when you need to answer questions"
        "Input should be a search query."
    )
    fn: Callable[[str], List[SearchResult]]

    @classmethod
    def from_engine_name(cls, engine_name: Literal['google', 'bing', 'duckduckgo', 'tavily', 'searx', 'brave'],
                         num_results: int):
        fn = get_search_fn(engine_name, num_results)
        return cls(fn=fn)

    def _run(self, query: str) -> List[Document]:
        results = self.fn(query)
        docs = []
        for res in results:
            res.update(**collect_url_content(res['link']))
            doc = Document(metadata=res)
            docs.append(doc)
        return docs


@tool
def search_with_wiki(query: str) -> List[Document]:
    """"A wrapper around Wikipedia. Useful for when you need to answer general questions about
    people, places, companies, facts, historical events, or other subjects. Input should be a search query."""
    page_titles = wiki_wrapper.wiki_client.search(
        query[:wiki_wrapper.WIKIPEDIA_MAX_QUERY_LENGTH], results=wiki_wrapper.top_k_results
    )
    docs = []
    for page_title in page_titles[: wiki_wrapper.top_k_results]:
        wiki_page = wiki_wrapper.wiki_client.page(title=page_title, auto_suggest=False)
        if wiki_page:
            wiki_page: WikipediaPage
            docs.append(Document(metadata=Metadata(
                content=wiki_page.html(),
                summary=wiki_page.summary,
                title=wiki_page.title,
                type='wiki',
                keywords='',
                source=wiki_page.url
            )))
    return docs


@tool
def search_with_arxiv(query: str) -> List[Document]:
    """A wrapper around Arxiv.org.Useful for when you need to answer questions about Physics, Mathematics,
    Computer Science, Quantitative Biology, Quantitative Finance, Statistics, Electrical Engineering, and Economics
    from scientific articles on arxiv.org.Input should be a search query."""
    if arxiv_wrapper.is_arxiv_identifier(query):
        results = arxiv_wrapper.arxiv_search(
            id_list=query.split(),
            max_results=arxiv_wrapper.top_k_results,
        ).results()
    else:
        results = self.arxiv_search(  # type: ignore
            query[: arxiv_wrapper.ARXIV_MAX_QUERY_LENGTH], max_results=3
        ).results()
    docs = []
    for res in results:
        res: Result
        res.categories.append(res.primary_category)
        keywords = ', '.join(res.categories)
        content = collect_pdf(url=res.pdf_url)
        doc = Document(metadata=Metadata(
            content=content,
            summary=res.summary,
            title=res.title,
            type='essay',
            keywords=keywords,
            source=res.pdf_url
        ))
        docs.append(doc)
    return docs


@tool
def generate_sub_query(queries: List[str]) -> List[Query]:
    """Generate 3 sub-queries for Internet searches when the information queried is too complex or unclear"""
    return queries
