from pymorphy2 import MorphAnalyzer

from krasoteevo.visualization import show
from krasoteevo.examples import get_example_graph
from krasoteevo.sentence_graph import SentenceGraph


class QUESTION_TYPES:
    WHICH = 'какой'
    WHO = 'кто'
    HOW_MANY = 'сколько'
    WHERE = 'где'
    WHEN = 'когда'
    WHERE_FROM = 'откуда'
    WHERE_TO = 'куда'
    WHY = 'почему'


class Question:
    def __init__(self, question_type: str):
        self.question_type = question_type


def print_questions(g: SentenceGraph):
    for vertex in g.vs:
        if vertex['is_word']:
            morph_info: SentenceGraph.MorphInfo = vertex['morph_info_list'][0]
            pos = morph_info.tags.POS
            edge_types = set([edge['type'] for edge in g.es.select(_source=vertex['id'])])

            if pos == 'NOUN':
                word = analyzer.parse(morph_info.word)[0]
                if morph_info.tags.number == 'plur' and 'опред' not in edge_types:
                    which = analyzer.parse(QUESTION_TYPES.WHICH)[0].inflect({'nomn', 'plur'})
                    word = word.inflect({'nomn'})
                    print(f'{which.word.capitalize()} {word.word}?')
                elif 'опред' not in edge_types:
                    which = analyzer.parse(QUESTION_TYPES.WHICH)[0].inflect({'nomn', 'masc', 'sing'})
                    which = which.inflect({word.tag.number, word.tag.gender})
                    word = word.inflect({'nomn'})
                    print(f'{which.word.capitalize()} {word.word}?')

                if morph_info.tags.number == 'plur' and QUESTION_TYPES.HOW_MANY not in edge_types:
                    word = analyzer.parse(morph_info.word)[0]
                    word = word.inflect({'gent'})
                    print(f'{QUESTION_TYPES.HOW_MANY.capitalize()} {word.word}?')

            elif pos in {'VERB', 'GRND', 'PRTF'}:
                if 'обст' not in edge_types:
                    print('Когда это произошло?')
                    print('Где это произошло?')
                    print('Почему это произошло?')
            elif pos == 'NUMR':
                if morph_info.word in {'двое', 'трое'} or morph_info.word[-1:] == 'о' and '1-компл' not in edge_types:
                    print('Кого', morph_info.word)


if __name__ == '__main__':
    analyzer = MorphAnalyzer()

    number = 0
    graph = get_example_graph(0, tag_class=analyzer.TagClass)

    print_questions(graph)
    print('\n', graph['json'])
    show(graph)

