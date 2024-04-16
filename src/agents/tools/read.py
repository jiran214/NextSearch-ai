#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import List

from langchain_core.tools import tool

from documents import Query, Document


@tool
def generate_new_questions(questions: List[Query]) -> List[Query]: return questions

@tool
def find_valuable_source(links: List[Query]) -> List[Document]: ...

@tool
def stop_and_delete(reason: str) -> None: return