#!/usr/bin/env python
# -*- coding: utf-8 -*-
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI


def create_agent(system, tools):
    llm = ChatOpenAI()
    prompt = ChatPromptTemplate.from_messages([("system", system), ("human", "{context}")])
    agent = create_tool_calling_agent(llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools)


