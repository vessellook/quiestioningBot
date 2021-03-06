from pprint import pprint

from igraph import Vertex
from pymorphy2 import MorphAnalyzer

from krasoteevo.examples import get_example_graph
from krasoteevo.sentence_graph import SentenceGraph
from krasoteevo.visualization import show
from parse_proxy.question_type import QuestionType as QType
from parse_proxy.complex_verb import ComplexVerb
from parse_proxy.morph_info import MorphInfo
from parse_proxy import ParseProxy
from predicates import is_present, is_move_verb, is_feeling_verb


class Question:
    def __init__(self, question_type: QType, target_word: ParseProxy, target_vertex: Vertex):
        self.question_type = question_type
        self.target_parse = target_word

    def __str__(self):
        if self.question_type is QType.WHICH:
            if {'NOUN', 'plur'} in self.target_parse.tag:
                word = self.target_parse.inflect({'nomn'})
                question = QType.WHICH.inflect({'plur'})
                return f'{question.word.capitalize()} {word.word}?'
            if {'NOUN'} in self.target_parse.tag:
                gender = self.target_parse.tag.gender if self.target_parse.tag.gender is not None\
                    else 'masc'
                question = QType.WHICH.inflect({gender})
                word = self.target_parse.inflect({'nomn'})
                return f'{question.word.capitalize()} {word.word}?'
            raise Warning('Unreachable point')
        if self.question_type is QType.HOW_MANY:
            if 'NOUN' in self.target_parse.tag:
                word = self.target_parse.inflect({'gent'})
                return f'{QType.HOW_MANY.word.capitalize()} {word.word}?'
            raise Warning('Unreachable point')
        if self.question_type is QType.WHERE_FROM:
            if 'VERB' in self.target_parse.tag:
                return f'{QType.WHERE_FROM.word.capitalize()} {self.target_parse.word}?'
            raise Warning('TODO: add support for GRND and PRTF (PRTS)')
        elif self.question_type is QType.WHERE_TO:
            if 'VERB' in self.target_parse.tag:
                return f'{QType.WHERE_TO.word.capitalize()} {self.target_parse.word}?'
        elif self.question_type is QType.WHERE:
            if 'VERB' in self.target_parse.tag:
                return f'{QType.WHERE.word.capitalize()} {self.target_parse.word}?'
        elif self.question_type is QType.HOW:
            if 'VERB' in self.target_parse.tag:
                return f'{QType.HOW.word.capitalize()} {self.target_parse.word}?'
        elif self.question_type is QType.WHEN:
            if 'VERB' in self.target_parse.tag:
                if {'past', 'impf'} in self.target_parse.tag:
                    return '?????????? ?????? ???????????????????????'
                if {'past', 'perf'} in self.target_parse.tag:
                    return '?????????? ?????? ???????????????????'
                if {'futr', 'perf'} in self.target_parse.tag:
                    return '?????????? ?????? ?????????????????????'
        elif self.question_type is QType.WHO:
            if 'NUMR' in self.target_parse.tag:
                return f'{QType.WHO.inflect("gent").word.capitalize()} {self.target_parse.word}?'
        return f"???? ????????: {self.question_type.word} {self.target_parse.word} " \
               f"{self.target_parse.tag}"


TIME_ADVERBS = ('??????????????????????', '????????????', '??????????????', '??????????', '??????????????????')

TIME_PHRASES = ('??????', '????????', '????????', '????????', '???? ?????????? ??????',
                '?????????? ??????')


def verb(vertex: Vertex, word: ParseProxy, analyzer: MorphAnalyzer):
    question_types = {QType.HOW, QType.WHEN, QType.WHERE, QType.WHERE_TO,
                      QType.WHERE_FROM}
    edges = vertex.out_edges()
    for edge in edges:
        child = edge.graph.vs[edge.target]['morph_info_list'][0]
        if 'INFN' in child.tag:
            word = ComplexVerb(word, child)
            break
    if is_present(word):
        question_types.discard(QType.WHEN)
    if is_move_verb(word, analyzer):
        question_types.discard(QType.WHERE)
        question_types.discard(QType.HOW)
    elif is_feeling_verb(word, analyzer):
        question_types.difference_update({QType.WHERE_FROM, QType.WHERE_TO, QType.WHERE})
    else:
        question_types.discard(QType.WHERE_FROM)
        question_types.discard(QType.WHERE_TO)
    for edge in edges:
        if edge['type'] != '????????':
            continue
        child = edge.graph.vs[edge.target]['morph_info_list'][0]
        if child.word in TIME_ADVERBS:
            question_types.discard(QType.WHEN)
        elif 'ADVB' in child.tag:
            question_types.discard(QType.HOW)
        else:
            question_types.discard({QType.WHERE_FROM, QType.WHERE_TO, QType.WHERE, QType.WHEN,
                                    QType.WHY})
    return [Question(question_type, word, vertex) for question_type in question_types]


def noun(vertex: Vertex, morph_info: ParseProxy, analyzer: MorphAnalyzer):
    word = analyzer.parse(morph_info.word)[0]
    edge_types = [edge['type'] for edge in vertex.out_edges()]
    questions = [Question(QType.WHICH, word, vertex)]

    if morph_info.tag.number == 'plur' and '????????????????' not in edge_types:
        questions.append(Question(QType.HOW_MANY, word, vertex))
    return questions


def get_questions(graph: SentenceGraph, analyzer: MorphAnalyzer):
    questions = []
    for vertex in graph.vs:
        if not vertex['is_word']:
            continue
        morph_info: MorphInfo = vertex['morph_info_list'][0]

        if 'NOUN' in morph_info.tag:
            questions.extend(noun(vertex, morph_info, analyzer))
        elif morph_info.tag.POS in {'VERB', 'GRND', 'PRTF', 'PRTS'}:
            if {'1per'} in morph_info.tag:
                morph_info = morph_info.inflect({'2per'})
            questions.extend(verb(vertex, morph_info, analyzer))
        elif 'NUMR' in morph_info.tag:
            if morph_info.normal_form in {'????????', '????????'} or morph_info.normal_form[-1:] == '??':
                questions.append(Question(QType.WHO, morph_info, vertex))
    return questions


def main():
    analyzer = MorphAnalyzer()
    QType.init(analyzer)

    # sentence = input()
    # graph = SentenceGraph(sentence, analyzer=analyzer)
    number = 5
    graph = get_example_graph(number, analyzer=analyzer)

    pprint([str(question) for question in get_questions(graph, analyzer=analyzer)])
    # pprint(graph['json'])
    show(graph)


if __name__ == '__main__':
    main()
