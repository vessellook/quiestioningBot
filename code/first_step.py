from pymorphy2 import MorphAnalyzer
from pymorphy2.analyzer import Parse

from krasoteevo.visualization import show
from krasoteevo.examples import get_example_graph
from krasoteevo.sentence_graph import SentenceGraph
from krasoteevo.tools import cut_affix


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


MOVE_VERBS = ['бежать', 'бегать', 'ехать', 'ездить', 'идти', 'ходить', 'лететь', 'летать',
              'плыть', 'плавать', 'тащить', 'таскать', 'катить', 'катать', 'катиться', 'кататься',
              'нести', 'носить', 'нестись', 'носиться', 'вести', 'водить', 'везти', 'возить',
              'ползти', 'ползать', 'лезть', 'лазить', 'лазать', 'брести', 'бродить', 'гнать',
              'гонять', 'гнаться', 'гоняться', 'йти']


def print_questions(g: SentenceGraph):
    for vertex in g.vs:
        if vertex['is_word']:
            morph_info: SentenceGraph.MorphInfo = vertex['morph_info_list'][0]
            edge_types = [edge['type'] for edge in vertex.out_edges()]

            if 'NOUN' in morph_info.tag:
                word = analyzer.parse(morph_info.word)[0]
                if 'plur' in morph_info.tag and 'опред' not in edge_types:
                    which = analyzer.parse(QUESTION_TYPES.WHICH)[0].normalized.inflect({'plur'})
                    word = word.inflect({'nomn'})
                    print(f'{which.word.capitalize()} {word.word}?')
                elif 'опред' not in edge_types:
                    which = analyzer.parse(QUESTION_TYPES.WHICH)[0].normalized
                    gender = word.tag.gender if word.tag.gender is not None else 'masc'
                    which = which.inflect({gender})
                    word = word.inflect({'nomn'})
                    print(f'{which.word.capitalize()} {word.word}?')

                if morph_info.tag.number == 'plur' and 'количест' not in edge_types:
                    word = analyzer.parse(morph_info.word)[0]
                    word = word.inflect({'gent'})
                    print(f'{QUESTION_TYPES.HOW_MANY.capitalize()} {word.word}?')

            elif morph_info.tag.POS in {'VERB', 'GRND', 'PRTF', 'PRTS'}:
                additional = ''
                for num, edge_type in enumerate(edge_types):
                    child = g.vs[vertex.out_edges()[num].target]['morph_info_list'][0]
                    if 'INFN' in child.tag:
                        additional = child.word
                        break
                normal_form = analyzer.parse(morph_info.word)[0].normal_form
                normal_form2 = cut_affix(normal_form, morph=analyzer)
                if type(normal_form2) != list:
                    normal_form = normal_form2
                if normal_form in MOVE_VERBS:
                    if 'обст' not in edge_types:
                        if 'past' in morph_info.tag:
                            print('Когда это произошло?')
                            print(f'Откуда {morph_info.word} {additional}?')
                            print(f'Куда {morph_info.word} {additional}?')
                            print(f'Как {morph_info.word} {additional}?')
                        elif {'futr', 'perf'} in morph_info.tag:
                            print('Когда это произойдёт?')
                            print(f'Откуда {morph_info.word} {additional}?')
                            print(f'Куда {morph_info.word} {additional}?')
                            print(f'Как {morph_info.word} {additional}?')
                        else:
                            print(f'Откуда {morph_info.word} {additional}?')
                            print(f'Куда {morph_info.word} {additional}?')
                            print(f'Как {morph_info.word} {additional}?')
                    else:
                        forbidden = ['завтра', 'сегодня', 'вчера']
                        where_allowed = True
                        for num, edge_type in enumerate(edge_types):
                            if edge_type == 'обст':
                                edge = vertex.out_edges()[num]
                                child = g.vs[edge.target]
                                if 'ADVB' not in child['morph_info_list'][0].tag:
                                    where_allowed = False
                        if vertex['token'] in forbidden:
                            where_allowed = False
                        if where_allowed:
                            if 'past' in morph_info.tag:
                                print('Когда это произошло?')
                                print(f'Откуда {morph_info.word} {additional}?')
                                print(f'Куда {morph_info.word} {additional}?')
                                print(f'Как {morph_info.word} {additional}?')
                            elif {'futr', 'perf'} in morph_info.tag:
                                print('Когда это произойдёт?')
                                print(f'Откуда {morph_info.word} {additional}?')
                                print(f'Куда {morph_info.word} {additional}?')
                                print(f'Как {morph_info.word} {additional}?')
                            else:
                                print(f'Откуда {morph_info.word} {additional}?')
                                print(f'Куда {morph_info.word} {additional}?')
                                print(f'Как {morph_info.word} {additional}?')
                else:
                    if 'обст' not in edge_types:
                        if 'past' in morph_info.tag:
                            print('Когда это произошло?')
                            print(f'Где {morph_info.word} {additional}?')
                            print(f'Как {morph_info.word} {additional}?')
                        elif {'futr', 'perf'} in morph_info.tag:
                            print('Когда это произойдёт?')
                            print(f'Где {morph_info.word} {additional}?')
                            print(f'Как {morph_info.word} {additional}?')
                        else:
                            print(f'Где {morph_info.word} {additional}?')
                            print(f'Как {morph_info.word} {additional}?')
                    else:
                        how_allowed = True
                        where_allowed = True
                        for num, edge_type in enumerate(edge_types):
                            if edge_type == 'обст':
                                edge = vertex.out_edges()[num]
                                child = g.vs[edge.target]
                                if 'ADVB' in child['morph_info_list'][0].tag:
                                    how_allowed = False
                                else:
                                    where_allowed = False
                        if how_allowed:
                            if 'past' in morph_info.tag:
                                print(f'Как {morph_info.word} {additional}?')
                            elif {'futr', 'perf'} in morph_info.tag:
                                print(f'Как {morph_info.word} {additional}?')
                            else:
                                print(f'Как {morph_info.word} {additional}?')
                        if where_allowed:
                            if 'past' in morph_info.tag:
                                print('Когда это произошло?')
                                print(f'Где {morph_info.word} {additional}?')
                            elif {'futr', 'perf'} in morph_info.tag:
                                print('Когда это произойдёт?')
                                print(f'Где {morph_info.word} {additional}?')
                            else:
                                print(f'Где {morph_info.word} {additional}?')
            elif 'NUMR' in morph_info.tag:
                if morph_info.word in {'двое', 'трое'} or morph_info.word[-1:] == 'о' and '1-компл' not in edge_types:
                    print('Кого', morph_info.word)
            else:
                print(morph_info.word, morph_info.tag)


if __name__ == '__main__':
    analyzer = MorphAnalyzer()

    sentence = input()
    graph = SentenceGraph(sentence, tag_class=analyzer.TagClass)
    # number = 27
    # graph = get_example_graph(number, tag_class=analyzer.TagClass)

    print_questions(graph)
    print('\n', graph['json'])
    show(graph)
