"""Classes to use syntax analysis results"""

import json
from typing import Any

from igraph import Graph

from krasoteevo.request import request_syntax_analysis


class SentenceGraph(Graph):
    """
    Class representing syntax analysis results

    It is the descendant of class igraph.Graph
    This class provides some graph, vertex and edge attributes

    Graph attribute 'sentence' is an initial sentence

>>> my_sentence = 'Ваня идёт гулять.'
>>> graph = SentenceGraph(my_sentence)
>>> graph['sentence']
'Ваня идёт гулять.'

    Graph attribute 'json' is a JSON object, parsed by service http://krasoteevo.ru

>>> my_sentence = 'Ваня идёт гулять.'
>>> graph = SentenceGraph(my_sentence)
>>> graph['json']
{'sentence': 'Ваня идёт гулять.', 'tokens': ['Ваня', 'идёт', 'гулять', '.'],
'morphs': [
[{'word': 'ваня', 'lexem': 'ваня', 'tag': "OpencorporaTag('NOUN,anim,masc,Name sing,nomn')"}],
[{'word': 'идёт', 'lexem': 'идти', 'tag': "OpencorporaTag('VERB,impf,intr sing,3per,pres,indc')"}],
[{'word': 'гулять', 'lexem': 'гулять', 'tag': "OpencorporaTag('INFN,impf,intr')"}], []],
'synts': [[1, 0, 'предик', 'идёт', 'ваня'], [1, 2, 'обст', 'идёт', 'гулять']]}

    Vertex attribute 'token' is unmodified word (even case of symbols isn't changed)

    Vertex attribute 'is_word' equal to True for word tokens and False for punctuation marks

    Vertex attribute 'morph_info_list' is None for punctuation marks
     and list of SentenceGraph.MorphInfo objects for word tokens

    Edge attribute 'type' is the type of connection between words, such as 'предик, 'обст', 'сочин',
    'соч-союз', '1-компл', 'огранич', 'предл', etc

    """

    class MorphInfo:
        """Class representing morphological information about word"""

        def __init__(self, word: str, lexeme: str, tag: str, tag_class: type = None):
            """

            :param word: word in some form
            :param lexeme: word in the main form
            :param tag: string of word tag in special format. Example of format:
                         <i>OpencorporaTag('NOUN,inan,masc sing,accs')<i/>
            :param tag_class: it is OpencorporaTag class passed from pymorphy2
             (see <a href="https://pymorphy2.readthedocs.io/en/stable/user/guide.html#id4">
             docs about OpencorporaTag class</a>).
            """
            self.word = word
            self.lexeme = lexeme
            left = "OpencorporaTag('"
            right = "')"
            self.raw_tag = tag[len(left):-len(right)]
            if tag_class is not None:
                self.tag = tag_class(self.raw_tag)
            else:
                self.tag = None

    def __init__(self, sentence: Any, tag_class: type = None):
        """
        :param sentence: a sentence to parse. Instead of string sentence, it can be
         a JSON object
        """
        if isinstance(sentence, str):
            try:
                # JSON string passed
                json_obj = json.loads(sentence)
            except json.JSONDecodeError:
                # sentence passed
                response = request_syntax_analysis(sentence)
                json_obj = response.json()
        else:
            # JSON object passed
            json_obj = sentence
        sentence = json_obj['sentence']

        vertex_count, vertex_attrs = _extract_vertices(json_obj, tag_class)
        edges, edge_attrs = _extract_edges(json_obj)

        super().__init__(self, directed=True, graph_attrs={'json': json_obj, 'sentence': sentence},
                         n=vertex_count, vertex_attrs=vertex_attrs,
                         edges=edges, edge_attrs=edge_attrs)


def _extract_vertices(json_obj, tag_class: type = None):
    def get_attrs(mi_list):
        if len(mi_list) > 0:
            # word token
            mi_list_converted = []
            for item in mi_list:
                morph_info = SentenceGraph.MorphInfo(word=item['word'], lexeme=item['lexem'],
                                                     tag=item['tags'], tag_class=tag_class)
                mi_list_converted.append(morph_info)
            return mi_list_converted, True
        # punctuation mark
        return None, False

    attrs = {'morph_info_list': [], 'is_word': [], 'token': [], 'id': []}
    for token, morph_info_list, num in zip(json_obj['tokens'], json_obj['morphs'], range(len(json_obj['morphs']))):
        attrs['token'].append(token)
        morph_info_list, is_word = get_attrs(morph_info_list)
        attrs['morph_info_list'].append(morph_info_list)
        attrs['is_word'].append(is_word)
        attrs['id'].append(num)
    return len(attrs), attrs


def _extract_edges(json_obj):
    edges = []
    attrs = {'type': []}
    for item in json_obj['synts']:
        edges.append((item[0], item[1]))
        attrs['type'].append(item[2])
    return edges, attrs
