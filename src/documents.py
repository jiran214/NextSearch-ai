#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass, field
from typing import TypedDict, List, Literal, Union, Optional

from langchain_core.documents import Document as LangchainDocument


class DocumentMetadata(TypedDict):
    abstract: str
    content: str
    source: dict


class Document(LangchainDocument):
    metadata: DocumentMetadata


Query = str
NodeDataType = Union[Document, Query]


@dataclass
class Node:
    data: NodeDataType
    parent: Optional['Node'] = None
    child_nodes: List['Node'] = field(default_factory=list)

    @property
    def node_type(self) -> Literal['Document', 'Query']:
        if isinstance(self.data, Document):
            return 'Document'
        return 'Query'

    def add_child_nodes(self, dataset: List[NodeDataType]):
        nodes = []
        for data in dataset:
            nodes.append(Node(data=data, parent=self))
        self.child_nodes.extend(nodes)

    def all_nodes(self):
        nodes = []
        nodes.append(self)
        for node in self.child_nodes:
            nodes.extend(node.all_nodes())
        return nodes

    def all_documents(self) -> List[Document]:
        nodes = self.all_nodes()
        return [node.data for node in nodes if node.node_type == 'Document']


@dataclass
class Tree:
    root: 'Node'
    leaf_nodes: List[Node] = field(default_factory=list)
    doc_node_num: int = field(default=0)

    def add_nodes(self, parent: Node, dataset: List[NodeDataType]):
        self.doc_node_num += len([data for data in dataset if isinstance(data, Document)])
        parent.add_child_nodes(dataset=dataset)
        self.leaf_nodes.extend(parent.child_nodes)

    def all_nodes(self):
        return self.root.all_nodes()

    def all_documents(self) -> List[Document]:
        return self.root.all_documents()
