#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from typing import Union, List

from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser
from langchain_core.agents import AgentAction, AgentFinish
from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import chain
from langchain_core.tools import BaseTool

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
            # print(f"Using {action.tool} input:{action.tool_input}")
            logger.info(f"Using {action.tool} input:{action.tool_input}")
            tool_output = tool.run(action.tool_input)
            if tool_output:
                docs.extend(get_list(tool_output))
        return docs or None
    return fn


def create_agent(system, tools, llm: BaseLanguageModel):
    prompt = ChatPromptTemplate.from_messages([
        ("system", system + f'Please use {get_os_language()} language'),
        ("human", "{input}")
    ])
    tool_map = {tool.name: tool for tool in tools}
    agent = prompt | llm.bind_tools(tools) | OpenAIToolsAgentOutputParser() | tool_call(tool_map)
    return agent


def load_reading_tools():
    from agents.tools.read import generate_new_questions, find_valuable_source, stop_and_delete
    return [generate_new_questions, find_valuable_source, stop_and_delete]


def load_searching_tools(search_engine, num_results):
    from agents.tools.search import SearchEngine, search_with_arxiv, search_with_wiki, generate_sub_query
    return [
        SearchEngine.from_engine_name(search_engine, num_results),
        search_with_arxiv,
        search_with_wiki,
        generate_sub_query
    ]

