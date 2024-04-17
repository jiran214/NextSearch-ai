#!/usr/bin/env python
# -*- coding: utf-8 -*-
import functools
import logging
import math
from itertools import chain
from typing import List, Sequence, TypedDict, Optional, Literal

from langchain_core.documents import Document
from langchain_core.document_loaders import BaseLoader
from langchain_core.tools import BaseTool

import settings
from agents.factory import create_agent, load_reading_tools, load_searching_tools
from documents import Node, Tree, NodeDataType

logger = logging.getLogger(__name__)


class ConfigDict(TypedDict):
    max_documents: float
    max_tokens: int
    llm: str
    reader_prompt: str
    searcher_prompt: str
    search_engine: Literal['google', 'bing', 'duckduckgo']


class WebDataMinerLoader(BaseLoader):
    def __init__(self, query: str, config: ConfigDict):
        self.query = query
        self.config = config
        self.tree = Tree(root=Node(data=self.query, parent=None), model_name=config.get('llm') or 'gpt-3.5-turbo')
        self.reader_prompt = self.config.get('reader_prompt') or settings.READER_PROMPT
        self.searcher_prompt = self.config.get('searcher_prompt') or settings.SEARCHER_PROMPT
        self.max_documents = self.config.get('max_documents') or math.inf
        self.max_tokens = self.config.get('max_tokens') or math.inf

        self.search_tools: List[BaseTool] = load_searching_tools(self.config.get('search_engine') or settings.DEFAULT_SEARCH_ENGINE)
        self.read_tools: List[BaseTool] = load_reading_tools()

    @property
    def run_info(self):
        return {
            'tokens': self.tree.tokens,
            'doc_node_num': self.tree.doc_node_num
        }

    def load(self) -> List[Document]:
        for tool in chain(self.read_tools, self.search_tools):
            tool.return_direct = True
        reader = create_agent(self.reader_prompt, self.read_tools)
        searcher = create_agent(self.searcher_prompt, self.search_tools)

        while self.tree.leaf_nodes:
            node = self.tree.leaf_nodes.pop()

            if node.node_type == 'Document':
                # 处理Document
                agent = reader
                context = node.data
            else:
                # 处理query
                agent = searcher
                context = node.data

            dataset: Optional[List[NodeDataType]] = agent.invoke({'input': context})
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