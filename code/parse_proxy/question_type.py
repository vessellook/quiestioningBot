from enum import Enum

from pymorphy2 import MorphAnalyzer

from .parse_proxy import choose_parse


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

    def __new__(cls, value):
        self = object.__new__(cls)
        self._value_ = value['word']
        self.word = value['word']
        self.raw_tag = value['tag']
        self.normal_form = value.get('normal_form', value['word'])
        return self       

    def __init__(self, value):
        self._parse = None
        self._morph = None

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
            item._morph = analyzer
            item._parse = choose_parse(word=item.word, tag=item.raw_tag,
                                       normal_form=item.normal_form, analyzer=analyzer)

