#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import List

from documents import Metadata


class SearchAPIAdapter:
    def run(self, query: str) -> List[Metadata]:
        ...