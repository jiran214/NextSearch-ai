#!/usr/bin/env python
# -*- coding: utf-8 -*-
import functools
import logging
from typing import List, Sequence, TypedDict

from langchain_core.documents import Document
from langchain_core.document_loaders import BaseLoader

from actions import ACTIONS_QUEUE
from documents import Node, NodeDataType, Tree

logger = logging.getLogger(__name__)


class ConfigDict(TypedDict):
    max_documents: float
    max_tokens: int


def discover_by_rules(data: NodeDataType) -> List[NodeDataType]:
    for action_cls in ACTIONS_QUEUE:
        action = action_cls(data)
        if action.match():
            return action.run()


def discover_by_agent():
    choose_tool = ...
    return choose_tool.run()


class WebDataMinerLoader(BaseLoader):
    def __init__(self, query: str, config: ConfigDict):
        self.query = query
        self.config = config

    def load(self) -> List[Document]:
        tree = Tree(root=Node(data=self.query, parent=None))
        while tree.leaf_nodes:
            node = tree.leaf_nodes.pop()
            dataset = discover_by_rules(node.data)
            if not dataset:
                continue
            if not isinstance(dataset, Sequence):
                dataset = [dataset]
            tree.add_nodes(node, dataset=dataset)
            if tree.doc_node_num >= self.config['max_documents']:
                break
            elif tree.tokens >= self.config['max_tokens']:
                break
        return tree.all_documents()
