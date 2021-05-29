from abc import abstractmethod
from typing import Protocol, Any, Optional

from pymorphy2 import MorphAnalyzer

from krasoteevo.krasoteevo_tag import KrasoteevoTag


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
    if isinstance(tag, KrasoteevoTag):
        tag = krasoteevo_to_pymorphy(tag)
    if isinstance(tag, str):
        tags = set(tag.replace(',', ' ').split(' '))
        for parse in analyzer.parse(word):
            print(tags)
            if tags in parse.tag and parse.normal_form == normal_form:
                return parse
    else:
        for parse in analyzer.parse(word):
            if parse.tag == tag and parse.normal_form == normal_form:
                return parse
    raise RuntimeError("No parse matches")


def krasoteevo_to_pymorphy(raw_tags: KrasoteevoTag):
    tags = set(raw_tags.split(' '))
    if 'ПРИЧ' in tags or 'ДЕЕПР' in tags or 'ИНФ' in tags:
        tags.discard('V')
    if 'A' in tags and 'КР' in tags:
        tags.add('A-КР')
    if 'S' in tags:
        tags.add('NPRO')
    return ' '.join(KRASOTEEVO_TO_PYMORPHY[tag] for tag in tags if tag in KRASOTEEVO_TO_PYMORPHY)


KRASOTEEVO_TO_PYMORPHY = {
    # "S": "NOUN" or "NPRO",
    "V": "VERB",
    "ADV": "ADVB",
    "PR": "PREP",
    "PART": "PRCL",
    "CONJ": "CONJ",
    "ПРИЧ": "PRTF",
    "ИНФ": "INFN",
    "A": "ADJF",
    "A-КР": "ADJS",
    "INTJ": "CONJ",
    "ЕД": "sing",
    "МН": "plur",
    "МУЖ": "masc",
    "ЖЕН": "femn",
    "СР": "neut",
    "ИМ": "nomn",
    "РОД": "gent",
    "ВИН": "accs",
    "ДАТ": "datv",
    "ТВОР": "ablt",
    "ПР": "loct",
    "ОД": "anim",
    "НЕОД": "inan",
    "ИЗЬЯВ": "indc",
    "СОВ": "perf",
    "ПРОШ": "past",
    "1-Л": "1per",
    "2-Л": "2per",
    "3-Л": "3per"
}
