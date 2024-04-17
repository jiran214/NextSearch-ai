#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from typing import List

from langchain_core.tools import tool

from agents.tools.parsers import collect_url_content
from documents import Query, Document


logger = logging.getLogger(__name__)

@tool
def generate_new_questions(questions: List[Query]) -> List[Query]:
    """When you have questions about the content of the article or have new ideas, please ask some new questions to
    use in Internet search"""
    return questions


@tool
def find_valuable_source(links: List[Query]) -> List[Document]:
    """Find valuable links in the resource and do a follow-up search"""
    docs = [Document(metadata=collect_url_content(url)) for url in links]
    return docs


@tool
def stop_and_delete(reason: str) -> None:
    """
    Use this tool to remove a resource when it is not relevant to the research topic, or when the quality of the
    resource is too poor
    Args:
        reason: reason of delete

    Returns:

    """
    return