#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import List

from documents import Query, Document


def generate_new_questions(questions: List[Query]) -> List[Query]: return questions
def find_valuable_source(links: List[Query]) -> List[Document]: ...
def stop_and_delete(reason: str) -> None: return