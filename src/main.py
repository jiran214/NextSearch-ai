#!/usr/bin/env python
# -*- coding: utf-8 -*-
import functools
import logging
import math
from itertools import chain
from typing import List, Sequence, TypedDict, Optional, Literal
from langchain_core.documents import Document
from langchain_core.document_loaders import BaseLoader
from langchain_core.language_models import BaseLanguageModel
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter

import settings
from agents.factory import create_agent, load_reading_tools, load_searching_tools
from documents import Node, Tree, NodeDataType

logger = logging.getLogger(__name__)


class ConfigDict(TypedDict):
    max_documents: float
    max_tokens: int
    embedding_model: str
    num_results: int
    reader_prompt: str
    searcher_prompt: str
    search_engine: Literal['google', 'bing', 'duckduckgo']
    openai_api_key: str


class SearchLoader(BaseLoader):
    def __init__(self, topic: str, config: ConfigDict, llm: Optional[BaseLanguageModel] = None):
        self.topic = topic.replace('\n', ' ')
        self.config = config
        self.tree = Tree(root=Node(data=self.topic, parent=None), embedding_model=config.get('embedding_model') or 'text-embedding-ada-002')
        self.reader_prompt = self.config.get('reader_prompt') or settings.READER_PROMPT
        self.searcher_prompt = self.config.get('searcher_prompt') or settings.SEARCHER_PROMPT
        self.max_documents = self.config.get('max_documents') or math.inf
        self.max_tokens = self.config.get('max_tokens') or math.inf
        self.search_tools: List[BaseTool] = load_searching_tools(
            self.config.get('search_engine') or settings.DEFAULT_SEARCH_ENGINE,
            config.get('num_results') or settings.NUM_RESULTS
        )
        self.read_tools: List[BaseTool] = load_reading_tools()
        self.llm = llm or ChatOpenAI(openai_api_key=self.config.get('openai_api_key'))

    @property
    def run_info(self):
        return {
            'tokens': self.tree.tokens,
            'doc_node_num': self.tree.doc_node_num
        }

    def load(self) -> List[Document]:
        for tool in chain(self.read_tools, self.search_tools):
            tool.return_direct = True
        reader = create_agent(self.reader_prompt, self.read_tools, self.llm)
        searcher = create_agent(self.searcher_prompt, self.search_tools, self.llm)

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

            dataset: Optional[List[NodeDataType]] = agent.invoke({'input': context, 'topic': self.topic})
            for data in dataset:
                if isinstance(data, Document):
                    logger.info(f"New Document: source={data.source} page_content={data.page_content}")
                else:
                    logger.info(f"New Query: {data}")

            if dataset is None:
                # 触发stop，删除节点
                node.delete()
                continue
            self.tree.add_nodes(node, dataset=dataset)
            if self.tree.doc_node_num >= self.max_documents:
                break
            elif self.tree.tokens >= self.max_tokens:
                break
        return self.tree.all_documents()


def split_large_chunk_and_save(docs: List[Document], max_chunk_size=4000, chunk_size=4000, chunk_overlap=0):
    splitter = RecursiveCharacterTextSplitter(
        separators=[f"<h{i}" for i in range(1, 5)] + ["<p"] + [
            '\n\n', '\n', '\r', '......', '!', '.', '。', '？', '！', '##'
        ],
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len
    )

