"""Classes to use syntax analysis results"""

import json
from typing import Any
from warnings import warn

from igraph import Graph
import pymorphy2

from parse_proxy.morph_info import MorphInfo
from krasoteevo.request import request_syntax_analysis


class SentenceGraph(Graph):
    """
    Class representing syntax analysis results

    It is the descendant of class `igraph.Graph`
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

    def __init__(self, sentence: Any = None, *args, analyzer: pymorphy2.MorphAnalyzer = None,
                 **kwargs):
        """
        :param sentence: a sentence to parse or JSON (string or object) from `krasoteevo.ru`
        :param analyzer: it is `pymorphy2.MorphAnlyzer` class passed from `pymorphy2`.
            It uses big dict (~15 GB) so the object of such class should be created one time
        """
        if sentence is not None:
            if isinstance(sentence, str):
                try:
                    # JSON string passed
                    json_obj = json.loads(sentence)
                except json.JSONDecodeError:
                    # sentence passed
                    response = request_syntax_analysis(sentence, old_format=True)
                    json_obj = response.json()
            else:
                # JSON object passed
                json_obj = sentence
            sentence = json_obj['sentence']
            if analyzer is None:
                warn("pymorphy2.MorphAnalyzer object has not been passed to SentenceGraph")
            vertex_count, vertex_attrs = _extract_vertices(json_obj, analyzer)
            edges, edge_attrs = _extract_edges(json_obj)

            super().__init__(self, directed=True, n=vertex_count, vertex_attrs=vertex_attrs,
                             graph_attrs={'json': json_obj, 'sentence': sentence},
                             edges=edges, edge_attrs=edge_attrs)
        else:
            super().__init__(self, *args, **kwargs)


_LEFT_OPENCORPORA_TAG = "OpencorporaTag('"
_RIGHT_OPENCORPORA_TAG = "')"


def _extract_vertices(json_obj, analyzer: pymorphy2.MorphAnalyzer = None):
    def clear(opencorpora_tag):
        return opencorpora_tag[len(_LEFT_OPENCORPORA_TAG):-len(_RIGHT_OPENCORPORA_TAG)]

    def get_attrs(mi_list):
        if isinstance(mi_list, dict):  # new JSON format
            mi_list = list(filter(lambda homonym: homonym['active'], mi_list['homonyms']))
        if mi_list:
            # word token
            mi_list_converted = []
            for item in mi_list:
                morph_info = MorphInfo(word=item['word'], normal_form=item['lexem'],
                                       grammemes=clear(item['tags']), analyzer=analyzer)
                mi_list_converted.append(morph_info)
            return mi_list_converted, True
            # punctuation mark
        return None, False

    attrs = {'morph_info_list': [], 'is_word': [], 'token': [], 'id': []}
    for num, (token, morph_info_list) in enumerate(zip(json_obj['tokens'], json_obj['morphs'])):
        attrs['token'].append(token)
        morph_info_list, is_word = get_attrs(morph_info_list)
        attrs['morph_info_list'].append(morph_info_list)
        attrs['is_word'].append(is_word)
        attrs['id'].append(num)
    return len(attrs['token']), attrs


def _extract_edges(json_obj):
    edges = []
    attrs = {'type': []}
    if not json_obj['synts']:
        return edges, attrs
    if isinstance(json_obj['synts'][0], list):
        synts_unique = set(((item[0], item[1], item[2]) for item in json_obj['synts']))
    elif isinstance(json_obj['synts'][0], dict):
        synts_unique = set(((item['head_i'], item['dependent_i'], item['dep_type']) for item in json_obj['synts']))
    else:
        raise Exception('bad format')
    for item in synts_unique:
        edges.append((item[0], item[1]))
        attrs['type'].append(item[2])
    return edges, attrs
