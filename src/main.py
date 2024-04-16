#!/usr/bin/env python
# -*- coding: utf-8 -*-
import functools
import logging
import math
from typing import List, Sequence, TypedDict, Optional

from langchain.agents import AgentExecutor
from langchain_core.documents import Document
from langchain_core.document_loaders import BaseLoader
from langchain_core.runnables import Runnable

import agents
import settings
from agents.factory import create_agent
from documents import Node, Tree, NodeDataType

logger = logging.getLogger(__name__)


class ConfigDict(TypedDict):
    max_documents: float
    max_tokens: int
    model_name: str
    reader_prompt: str
    searcher_prompt: str


class WebDataMinerLoader(BaseLoader):
    def __init__(self, query: str, config: ConfigDict):
        self.query = query
        self.config = config
        self.tree = Tree(root=Node(data=self.query, parent=None), model_name=config.get('model_name') or 'gpt-3.5-turbo')
        self.reader_prompt = self.config.get('reader_prompt') or settings.READER_PROMPT
        self.searcher_prompt = self.config.get('searcher_prompt') or settings.SEARCHER_PROMPT
        self.read_tools = []
        self.search_tools = []
        self.max_documents = self.config.get('max_documents') or math.inf
        self.max_tokens = self.config.get('max_tokens') or math.inf

    @property
    def run_info(self):
        return {
            'tokens': self.tree.tokens,
            'doc_node_num': self.tree.doc_node_num
        }

    def load(self) -> List[Document]:
        while self.tree.leaf_nodes:
            node = self.tree.leaf_nodes.pop()

            reader = create_agent(self.reader_prompt, self.read_tools)
            searcher = create_agent(self.searcher_prompt, self.search_tools)

            if node.node_type == 'Document':
                # 处理Document
                agent = reader
                context = node.data
            else:
                # 处理query
                agent = searcher
                context = node.data

            dataset: Optional[List[NodeDataType]] = agent.invoke({'context': context})
            if dataset is None:
                # 触发stop，删除节点
                node.delete()
                continue
            if not isinstance(dataset, Sequence):
                dataset = [dataset]
            self.tree.add_nodes(node, dataset=dataset)
            if self.tree.doc_node_num >= self.max_documents:
                break
            elif self.tree.tokens >= self.max_tokens:
                break
        return self.tree.all_documents()