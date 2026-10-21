import os
import re
import jieba
from rank_bm25 import BM25Okapi

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

_bm25 = None
_chunks = None


def _init_bm25():
    global _bm25, _chunks
    if _bm25 is None:
        manual_path = os.path.join(DATA_DIR, "manual.txt")
        if not os.path.exists(manual_path):
            return
        with open(manual_path, "r", encoding="utf-8") as f:
            content = f.read()

        # 按行切分手册
        _chunks = [c.strip() for c in content.split("\n") if c.strip()]
        # 用 jieba 分词构建本地索引
        tokenized_corpus = [list(jieba.cut(chunk)) for chunk in _chunks]
        _bm25 = BM25Okapi(tokenized_corpus)


def search_manual(query: str) -> str:
    """极简本地检索：优先正则精确匹配，其次走 BM25 语义匹配"""
    _init_bm25()
    if _bm25 is None:
        return "手册文件不存在。"

    # 1. 优先正则精确匹配
    match = re.search(r"ERR-\d{3}", query)
    if match:
        error_code = match.group(0)
        for chunk in _chunks:
            if error_code in chunk:
                return chunk

    # 2. 如果没匹配到错误码，走 BM25 模糊检索
    tokenized_query = list(jieba.cut(query))
    top_chunks = _bm25.get_top_n(tokenized_query, _chunks, n=1)
    if top_chunks:
        return top_chunks[0]

    return "未在手册中明确找到该错误码的说明。"