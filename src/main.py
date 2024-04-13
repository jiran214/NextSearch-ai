#!/usr/bin/env python
# -*- coding: utf-8 -*-
import functools
import logging
from typing import List, Sequence, TypedDict

from langchain_core.documents import Document
from langchain_core.document_loaders import BaseLoader

import agents
from documents import Node, NodeDataType, Tree

logger = logging.getLogger(__name__)


class ConfigDict(TypedDict):
    max_documents: float
    max_tokens: int
    model_name: str


def covert_node_2_context(node: Node) -> str:
    return ''


class WebDataMinerLoader(BaseLoader):
    def __init__(self, query: str, config: ConfigDict):
        self.query = query
        self.config = config
        self.tree = Tree(root=Node(data=self.query, parent=None), model_name=config["model_name"] or 'gpt-3.5-turbo')

    @property
    def run_info(self):
        return {
            'tokens': self.tree.tokens,
            'doc_node_num': self.tree.doc_node_num
        }

    def load(self) -> List[Document]:
        while self.tree.leaf_nodes:
            node = self.tree.leaf_nodes.pop()
            context = covert_node_2_context(node)
            dataset = agents.discover_agent.invoke({'context': context})
            if not dataset:
                continue
            if not isinstance(dataset, Sequence):
                dataset = [dataset]
            self.tree.add_nodes(node, dataset=dataset)
            if self.tree.doc_node_num >= self.config['max_documents']:
                break
            elif self.tree.tokens >= self.config['max_tokens']:
                break
        return self.tree.all_documents()
