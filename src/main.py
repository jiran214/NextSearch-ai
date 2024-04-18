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
    def __init__(self, topic: str, config: Optional[ConfigDict] = None, llm: Optional[BaseLanguageModel] = None):
        config = config or {}
        self.topic = topic.replace('\n', ' ')
        self.tree = Tree(root=Node(data=self.topic, parent=None), embedding_model=config.get('embedding_model') or 'text-embedding-ada-002')
        self.reader_prompt = config.get('reader_prompt') or settings.READER_PROMPT
        self.searcher_prompt = config.get('searcher_prompt') or settings.SEARCHER_PROMPT
        self.max_documents = config.get('max_documents') or math.inf
        self.max_tokens = config.get('max_tokens') or math.inf
        self.search_tools: List[BaseTool] = load_searching_tools(
            config.get('search_engine') or settings.DEFAULT_SEARCH_ENGINE,
            config.get('num_results') or settings.NUM_RESULTS
        )
        self.read_tools: List[BaseTool] = load_reading_tools()
        self.llm = llm or ChatOpenAI(openai_api_key=config.get('openai_api_key'))
        logger.info(f"SearchLoader initialize...")

        self.reader = create_agent(self.reader_prompt, self.read_tools, self.llm)
        self.searcher = create_agent(self.searcher_prompt, self.search_tools, self.llm)

    def load(self) -> List[Document]:
        logger.info(f"SearchLoader Start Running...")
        while self.tree.leaf_nodes:
            node = self.tree.leaf_nodes.pop()

            if node.node_type == 'Document':
                # 处理Document
                agent = self.reader
                context = node.data
            else:
                # 处理query
                agent = self.searcher
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
        separators=[
            "<p", '<h', '\n\n', '\n', '\r', '......', '!', '.', '。', '？', '！', '##'
        ],
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len
    )


if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    loader = SearchLoader('AI Agent', llm=ChatOpenAI(openai_api_base='https://oneapi.chatgo.io/v1', openai_api_key="""sk-PQpwCuGQrqWy5hhXD03fBd5c104e405093F3D8980bF5Ac7a"""))
    # print(loader.reader.invoke({'input': '```Rapping (also rhyming, flowing, spitting, emceeing or MCing) is an artistic form of vocal delivery and emotive expression that incorporates "rhyme, rhythmic speech, and [commonly] street vernacular". It is usually performed over a backing beat or musical accompaniment. The components of rap include "content" (what is being said, e.g., lyrics), "flow" (rhythm, rhyme), and "delivery" (cadence, tone). Rap differs from spoken-word poetry in that it is usually performed off-time to musical accompaniment. It also differs from singing, which varies in pitch and does not always include words. Because they do not rely on pitch inflection, some rap artists may play with timbre or other vocal qualities. Rap is a primary ingredient of hip hop music, and so commonly associated with that genre that it is sometimes called "rap music".\nPrecursors to modern rap music include the West African griot tradition, certain vocal styles of blues and jazz, an African-American insult game called playing the dozens (see Battle rap and Diss), and 1960s African-American poetry. Stemming from the hip-hop cultural movement, rap music originated in the Bronx, New York City, in the early 1970s and became part of popular music later that decade. Rapping developed from the role of master of ceremonies (MC) at parties within the scene, who would encourage and entertain guests between DJ sets, which evolved into longer performances.\nRap is usually delivered over a beat, typically provided by a DJ, turntablist, or beatboxer when performing live. Much less commonly a rapper can decide to perform a cappella, meaning without accompaniment of any sort, beat(s) included. When a rap or hip-hop artist is creating a song, "track", or record, done primarily in a production studio, most frequently a producer provides the beat(s) for the MC to flow over. Stylistically, rap occupies a gray area between speech, prose, poetry, and singing. The word, which predates the musical form, originally meant "to lightly strike", and is now used to describe quick speech or repartee. The word had been used in British English since the 16th century. It was part of the African American dialect of English in the 1960s meaning "to converse", and very soon after that came to denote the musical style. The word "rap" is so closely associated with hip-hop music that many writers use the terms interchangeably.```', 'topic': 'AI rap'}))
    print(loader.searcher.invoke({'input': 'AI rap singer list', 'topic': 'AI rap'}))
