"""Classes to use syntax analysis results"""

from typing import Any
from requests import Response

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
[{'word': 'ваня', 'lexem': 'ваня', 'tags': "OpencorporaTag('NOUN,anim,masc,Name sing,nomn')"}],
[{'word': 'идёт', 'lexem': 'идти', 'tags': "OpencorporaTag('VERB,impf,intr sing,3per,pres,indc')"}],
[{'word': 'гулять', 'lexem': 'гулять', 'tags': "OpencorporaTag('INFN,impf,intr')"}], []],
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
        def __init__(self, word: str, lexeme: str, tags: str):
            """

            :param word: word in some form
            :param lexeme: word in the main form
            :param tags: string of word tags in special format. Example of format:
                         <i>OpencorporaTag('NOUN,inan,masc sing,accs')<i/>
            """
            self.word = word
            self.lexeme = lexeme
            self.raw_tags = tags
            left = "OpencorporaTag('"
            right = "')"
            self.tags = tags[len(left):-len(right)].split(',')
            self.type = tags[0]

    def __init__(self, sentence: Any):
        """

        :param sentence: a sentence to parse. Instead of string sentence, it can be
         a JSON object
        """
        if isinstance(sentence, str):
            response = request_syntax_analysis(sentence)
            json_obj = response.json()
        else:
            json_obj = sentence
            sentence = json_obj['sentence']

        vertex_attrs = SentenceGraph._vertex_attrs(json_obj)
        edges, edge_attrs = SentenceGraph._edges(json_obj)

        super().__init__(self, directed=True, graph_attrs={'json': json_obj, 'sentence': sentence},
                         n=len(vertex_attrs), vertex_attrs=vertex_attrs,
                         edges=edges, edge_attrs=edge_attrs)

    @staticmethod
    def _vertex_attrs(json_obj):
        def get_attrs(mi_list):
            if len(mi_list) > 0:
                # word token
                mi_list = [SentenceGraph.MorphInfo(word=item['word'], lexeme=item['lexem'],
                                                   tags=item['tags']) for item in mi_list]
                return list(mi_list), True
            # punctuation mark
            return None, False

        attrs = {'morph_info_list': [], 'is_word': [], 'token': []}
        for token, morph_info_list in zip(json_obj['tokens'], json_obj['morphs']):
            attrs['token'].append(token)
            morph_info_list, is_word = get_attrs(morph_info_list)
            attrs['morph_info_list'].append(morph_info_list)
            attrs['is_word'].append(is_word)
            return attrs

    @staticmethod
    def _edges(json_obj):
        edges = []
        attrs = {'type': []}
        for item in json_obj['synts']:
            edges.append((item[0], item[1]))
            attrs['type'].append(item[2])
        return edges, attrs
