#!/usr/bin/env python
# -*- coding: utf-8 -*-
import locale
from typing import Sequence

import pycountry


def get_list(data):
    if not isinstance(data, Sequence):
        return [data]
    return data


def get_os_language():
    try:
        return pycountry.languages.get(alpha_2=locale.getdefaultlocale()[0].split('_')[0]).name
    except:
        return