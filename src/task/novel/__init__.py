"""
小说创作子包（原 novel_creation）
基于 ReAct 的中长篇小说创作系统
"""
from .react_novel_creator import ReactNovelCreator, NovelChapter

__all__ = [
    "ReactNovelCreator",
    "NovelChapter",
]
