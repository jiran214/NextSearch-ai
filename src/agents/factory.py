#!/usr/bin/env python
# -*- coding: utf-8 -*-
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI


def create_agent(system, tools):
    llm = ChatOpenAI()
    prompt = ChatPromptTemplate.from_messages([("system", system), ("human", "{input}")])
    agent = create_tool_calling_agent(llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools)


def load_reading_tools():
    from tools.read import generate_new_questions, find_valuable_source, stop_and_delete
    return [generate_new_questions(), find_valuable_source(), stop_and_delete()]


def load_searching_tools(search_engine):
    from tools.search import SearchEngine, search_with_arxiv, search_with_wiki, generate_sub_query
    return [SearchEngine.from_name(search_engine), search_with_arxiv(), search_with_wiki(), generate_sub_query()]

