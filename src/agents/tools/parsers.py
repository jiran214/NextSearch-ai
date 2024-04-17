#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
from newspaper import Article
from pydantic import AnyUrl

from documents import Metadata
from lxml.html.clean import Cleaner

setattr(Article, 'release_resources', lambda *args, **kwargs: None)


def clean_html(html_text, safe_attrs=None, remove_tags=None, kill_tags=None):
    if not html_text:
        return ""
    safe_attrs = set(safe_attrs or []) | {'src', 'href', 'alt', 'title', 'data-src'}
    kill_tags = set(kill_tags or []) | {'style', 'noscript'}
    remove_tags = set(remove_tags or []) | {'html', 'body', 'figure', 'div', 'section', 'noscript', 'footer'}
    cleaner = Cleaner(safe_attrs=safe_attrs, remove_tags=remove_tags, kill_tags=kill_tags)
    cleaned_html = cleaner.clean_html(html_text)
    if 'div' in (remove_tags or []):
        cleaned_html = cleaned_html.replace('<div>', '')
    cleaned_html = cleaned_html.replace("<img src="">", '').replace('<img alt="" src="" />', '').replace('<img src="">', '').replace('</div>', '').replace('<svg></svg>', '').replace('<span></span>', '').replace("<p></p>", '').strip()
    return cleaned_html


def collect_article(url: str) -> Metadata:
    url = AnyUrl(url)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0',
        'Origin': f'{url.scheme}://{url.host}'
    }
    r = requests.get(url, headers=headers)
    r.encoding = r.apparent_encoding
    if r.ok and (html := r.text):
        article = Article(str(url), keep_article_html=True)
        article.set_html(html)
        article.parse()
        if article.article_html:
            article.article_html = clean_html(article.article_html)
            return Metadata(
                content=article.article_html,
                summary=article.meta_description,
                title=article.title,
                type='web_page',
                keywords=article.keywords,
                link=str(url)
            )


def collect_url_content(url: str) -> Metadata:
    return collect_article(url)