"""This package contains interface ParseLike and classes with this interface"""
from abc import abstractmethod
from typing import Protocol, Any, Optional

from pymorphy2 import MorphAnalyzer


class ParseProxy(Protocol):
    """Interface for classes :class:`pymorphy2.analyzer.Parse`,
       :class:`ComplexVerb`, :class:`QuestionTypes` etc"""

    @abstractmethod
    def inflect(self, required_grammemes) -> 'ParseProxy':
        pass

    @property
    @abstractmethod
    def word(self) -> str:
        pass

    @property
    @abstractmethod
    def normal_form(self) -> str:
        pass

    @property
    @abstractmethod
    def tag(self):  # it can be object variable
        pass

    @property
    @abstractmethod
    def normalized(self) -> 'ParseProxy':
        """ A :class:`ParseLike` instance for :attr:`self.normal_form`"""

    @property
    @abstractmethod
    def _morph(self) -> Optional[MorphAnalyzer]:
        pass


def choose_parse(word: str, tag: Any, analyzer: MorphAnalyzer, normal_form: str = None):
    """Function to convert word to pymorphy2.Parse object"""
    if normal_form is None:
        normal_form = word
    if isinstance(tag, str):
        tag = analyzer.TagClass(tag)
    for parse in analyzer.parse(word):
        if parse.tag == tag and parse.normal_form == normal_form:
            return parse
    raise RuntimeError("No parse matches")
