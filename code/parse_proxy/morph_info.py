from pymorphy2 import MorphAnalyzer

from .parse_proxy import choose_parse


class MorphInfo:
    """Class representing morphological information about word"""

    def __init__(self, word: str, normal_form: str, grammemes: str,
                 analyzer: MorphAnalyzer = None):
        """
        :param word: word in some form
        :param normal_form: word in the normal form
        :param grammemes: string of word tags
        :param analyzer: `MorphAnalyzer` object passed
            from `pymorphy2`. It uses big dict (~15 GB) so the object
            of such class should be created one time
        """
        self._word = word
        self._normal_form = normal_form
        self.grammemes = grammemes
        if analyzer is None:
            self.tag = None
            self._parse = None
            self.analyzer = None
        else:
            print(grammemes, word)
            self._parse = choose_parse(word, tag=grammemes, normal_form=normal_form,
                                       analyzer=analyzer)
            self.tag = self._parse.tag
            self.analyzer = analyzer

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

    @property
    def _morph(self):  # I added this method to support ParseProxy interface
        return self.analyzer
