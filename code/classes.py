"""This module contains interface ParseLike and classes with this interface"""

from abc import abstractmethod
from enum import Enum
from typing import Protocol, Any

from pymorphy2 import MorphAnalyzer


class ParseLike(Protocol):
    """Interface for classes :class:`pymorphy2.analyzer.Parse`,
       :class:`ComplexVerb`, :class:`QuestionTypes` etc"""

    @abstractmethod
    def inflect(self, required_grammemes) -> 'ParseLike':
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
    def normalized(self) -> 'ParseLike':
        """ A :class:`ParseLike` instance for :attr:`self.normal_form`. """


class ComplexVerb:
    def __init__(self, modal: ParseLike, infinitive: ParseLike):
        self.modal = modal
        self.infinitive = infinitive

    def inflect(self, required_grammemes):
        new_modal = self.modal.inflect(required_grammemes)
        return ComplexVerb(new_modal, self.infinitive)

    @property
    def word(self):
        return f'{self.modal.word} {self.infinitive.word}'

    @property
    def tag(self):
        return self.modal.tag

    @property
    def normal_form(self):
        return f'{self.modal.normal_form} {self.infinitive.word}'

    @property
    def normalized(self):
        return ComplexVerb(self.modal.normalized, self.infinitive)


class QuestionType(Enum):
    WHICH = {'word': 'какой', 'tag': 'ADJF,Apro masc,sing,nomn'}
    WHO = {'word': 'кто', 'tag': 'NPRO,masc sing,nomn'}
    HOW_MANY = {'word': 'сколько', 'tag': 'ADVB'}
    WHERE = {'word': 'где', 'tag': 'ADVB,Ques'}
    WHEN = {'word': 'когда', 'tag': 'ADVB,Ques'}
    WHERE_FROM = {'word': 'откуда', 'tag': 'ADVB,Ques'}
    WHERE_TO = {'word': 'куда', 'tag': 'ADVB,Ques'}
    HOW = {'word': 'как', 'tag': 'ADVB,Ques'}
    WHY = {'word': 'почему', 'tag': 'ADVB,Ques'}

    def __init__(self, value):
        self._value_ = value['word']
        self.word = value['word']
        self.raw_tag = value['tag']
        self.normal_form = value['normal_form'] if 'normal_form' in value else value['word']
        self._parse = None

    def inflect(self, *args, **kwargs):
        return self._parse.inflect(*args, **kwargs)

    @property
    def normalized(self):
        return self._parse.normalized

    @property
    def tag(self):
        return self._parse.tag

    @classmethod
    def init(cls, analyzer: MorphAnalyzer):
        for item in cls:
            item._parse = choose_parse(word=item.word, tag=item.raw_tag,
                                       normal_form=item.normal_form, analyzer=analyzer)


class MorphInfo:
    """Class representing morphological information about word"""

    def __init__(self, word: str, normal_form: str, raw_tag: str,
                 analyzer: MorphAnalyzer = None):
        """
        :param word: word in some form
        :param normal_form: word in the normal form
        :param raw_tag: string of word tags
        :param analyzer: `MorphAnalyzer` object passed
            from `pymorphy2`. It uses big dict (~15 GB) so the object
            of such class should be created one time
        """
        self._word = word
        self._normal_form = normal_form
        self.raw_tag = raw_tag
        if analyzer is None:
            self.tag = None
            self._parse = None
        else:
            self.tag = analyzer.TagClass(self.raw_tag)
            self._parse = choose_parse(word, tag=self.tag, normal_form=normal_form, analyzer=analyzer)

    @property
    def word(self):
        return self._word

    @property
    def normal_form(self):
        return self._normal_form

    @property
    def normalized(self):
        return self._parse.normalized

    def inflect(self, required_grammemes):
        parse = self._parse.inflect(required_grammemes)
        return parse


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
