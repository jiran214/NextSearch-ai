#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from typing import Union, List

from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.agents import AgentAction, AgentFinish
from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import chain, Runnable
from langchain_core.tools import BaseTool

from agents.tools.parsers import ReadingResult
from utils import get_list, get_os_language

logger = logging.getLogger(__name__)


def tool_call(tool_map):
    @chain
    def fn(output: Union[List[AgentAction], AgentFinish]):
        if isinstance(output, AgentFinish):
            return
        docs = []
        for action in output:
            tool: BaseTool = tool_map[action.tool]
            logger.info(f"Using {action.tool} input:{action.tool_input}")
            tool_output = tool.run(action.tool_input)
            if tool_output:
                docs.extend(get_list(tool_output))
        return docs or None
    return fn


def create_searcher(system, tools, llm: BaseLanguageModel):
    prompt = ChatPromptTemplate.from_messages([
        ("system", system + f'Please use {get_os_language()} language'),
        ("human", "{input}")
    ])
    tool_map = {tool.name: tool for tool in tools}
    agent = prompt | llm.bind_tools(tools) | OpenAIToolsAgentOutputParser() | tool_call(tool_map)
    return agent


def create_reader(system, llm: BaseLanguageModel, schema=ReadingResult):
    parser = JsonOutputParser(pydantic_object=schema)
    prompt = ChatPromptTemplate.from_messages([
        ("system", system + f'Please use {get_os_language()} language'),
        ("human", "{input}\n" + parser.get_format_instructions())
    ])
    agent = prompt | llm | parser
    return agent


def create_workflow(searcher: Runnable, reader: Runnable):
    return searcher | reader


def load_searching_tools(search_engine, num_results):
    from agents.tools.search import SearchEngine, search_with_arxiv, search_with_wiki, generate_sub_query
    return [
        SearchEngine.from_engine_name(search_engine, num_results),
        search_with_arxiv,
        search_with_wiki,
        generate_sub_query
    ]

