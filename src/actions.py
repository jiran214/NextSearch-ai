#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import List, Union

from documents import Query, Document, NodeDataType


class Action:

    def __init__(self, data: NodeDataType):
        self.data = data
        self.action_result = None

    def match(self) -> bool: ...
    def run(self) -> Union[List[NodeDataType], NodeDataType]: ...


class SubQueryGeneration(Action):

    def match(self) -> bool:
        ...

    def run(self) -> List[Query]:
        ...


class NewQuestionsGeneration(Action):

    def match(self) -> bool:
        ...

    def run(self) -> List[Query]:
        ...


class LinkContentFinder(Action):

    def match(self) -> bool:
        ...

    def run(self) -> List[Query]:
        ...


class QuerySearch(Action):

    def match(self) -> bool:
        ...

    def run(self) -> List[Document]:
        ...


ACTIONS_QUEUE = [
    LinkContentFinder,
    QuerySearch,
    NewQuestionsGeneration,
    SubQueryGeneration,
]