from enum import Enum

from pymorphy2 import MorphAnalyzer

from krasoteevo.visualization import show
from krasoteevo.examples import get_example_graph
from krasoteevo.sentence_graph import SentenceGraph
from krasoteevo.tools import cut_affix, choose_parse


def question_types(analyzer: MorphAnalyzer):
    class QuestionTypes(Enum):
        WHICH = {'value': 'какой', 'tag': 'ADJF,Apro masc,sing,nomn'}
        WHO = {'value': 'кто', 'tag': 'NPRO,masc sing,nomn'}
        HOW_MANY = {'value': 'сколько', 'tag': 'ADVB'}
        WHERE = {'value': 'где', 'tag': 'ADVB,Ques'}
        WHEN = {'value': 'когда', 'tag': 'ADVB,Ques'}
        WHERE_FROM = {'value': 'откуда', 'tag': 'ADVB,Ques'}
        WHERE_TO = {'value': 'куда', 'tag': 'ADVB,Ques'}
        WHY = {'value': 'почему', 'tag': 'ADVB,Ques'}

        def __new__(cls, values):
            obj = object.__new__(cls)
            obj._value_ = values['value']
            obj.raw_tag = values['tag']
            obj.parse = choose_parse(word=values['value'], raw_tag=values['tag'], analyzer=analyzer)
            return obj

    return QuestionTypes


MOVE_VERBS = (
    'бегать', 'бежать', 'брести', 'бродить', 'везти', 'вести', 'водить', 'возить', 'гнать',
    'гнаться', 'гонять', 'гоняться', 'ездить', 'ехать', 'идти', 'йти', 'катать', 'кататься',
    'катить', 'катиться', 'лазать', 'лазить', 'лезть', 'летать', 'лететь', 'нести', 'нестись',
    'носить', 'носиться', 'плавать', 'плыть', 'ползать', 'ползти', 'таскать', 'тащить', 'ходить')

FEELING_VERBS = (
        'блаженствовать', 'боготворить', 'бояться',
        'брезговать', 'веселиться', 'взбудоражиться',
        'взволновать', 'влюблять', 'возбуждаться',
        'возмущать', 'возненавидеть', 'восторгаться',
        'восхищаться', 'восхищаться', 'всполошиться',
        'гневить', 'горевать', 'грустить', 'дивиться',
        'докучать', 'досадовать', 'досаждать', 'жалеть',
        'загореться', 'злить', 'злиться', 'злорадствовать',
        'изводить', 'измучиться', 'изнемогать', 'изнывать',
        'изумляться', 'интересоваться', 'испугаться',
        'конфузить', 'конфузиться', 'кручиниться', 'ласкать',
        'ликовать', 'любить', 'любоваться', 'маяться',
        'млеть', 'мущаться', 'невзлюбить', 'недолюбливать',
        'недоумевать', 'нежить', 'ненавидеть', 'нервничать',
        'нравиться', 'оберегать', 'обидеться', 'обижаться',
        'обнимать', 'ободриться', 'обожать', 'обозлиться',
        'огорчать', 'огорчаться', 'ожесточить', 'оживиться',
        'озлобить', 'омрачать', 'опасаться', 'опечалить',
        'опечалиться', 'опешить', 'опротиветь', 'осмелеть',
        'осмелиться', 'остерегаться', 'осудить', 'оторопеть',
        'очаровать', 'очароваться', 'переживать', 'печалить',
        'печалиться', 'пленять', 'повеселеть', 'покорять',
        'поразиться', 'почитать', 'презирать', 'приголубить',
        'пугаться', 'радоваться', 'развеяться', 'раздражать',
        'разъяриться', 'располагать', 'рассвирепеть',
        'рассердиться', 'расстроить', 'расстроиться',
        'расхрабриться', 'расшевелиться', 'робеть',
        'сердить', 'сердиться', 'сетовать', 'сжалиться',
        'симпатизировать', 'скучать', 'смелеть', 'смущать',
        'соболезновать', 'сожалеть', 'сокрушаться',
        'сопереживать', 'сострадать', 'сочувствовать',
        'стесняться', 'страдать', 'стыдиться', 'терзаться',
        'томить', 'томиться', 'торжествовать', 'тосковать',
        'трепетать', 'трусить', 'тушеваться', 'тяготиться',
        'уважать', 'увлекаться', 'удивляться', 'удручать',
        'унижать', 'усовестить', 'успокоиться', 'устыдить',
        'устыдиться', 'утешиться', 'уязвить', 'хандрить',
        'чествовать', 'чтить')

TIME_ADVERBS = ('послезавтра', 'завтра', 'сегодня', 'вчера', 'позавчера')


def get_questions(graph: SentenceGraph, analyzer: MorphAnalyzer, QuestionTypes: type):
    def noun():
        word = analyzer.parse(morph_info.word)[0]
        if 'plur' in morph_info.tag and 'опред' not in edge_types:
            which = analyzer.parse(QuestionTypes.WHICH.value)[0].normalized.inflect({'plur'})
            word = word.inflect({'nomn'})
            questions.append(f'{which.word.capitalize()} {word.word}?')
        elif 'опред' not in edge_types:
            which = analyzer.parse(QuestionTypes.WHICH.value)[0].normalized
            gender = word.tag.gender if word.tag.gender is not None else 'masc'
            which = which.inflect({gender})
            word = word.inflect({'nomn'})
            questions.append(f'{which.word.capitalize()} {word.word}?')

        if morph_info.tag.number == 'plur' and 'количест' not in edge_types:
            word = analyzer.parse(morph_info.word)[0]
            word = word.inflect({'gent'})
            questions.append(f'{QuestionTypes.HOW_MANY.value.capitalize()} {word.word}?')

    def verb(vertex):
        additional = ''
        for num, edge_type in enumerate(edge_types):
            child = graph.vs[vertex.out_edges()[num].target]['morph_info_list'][0]
            if 'INFN' in child.tag:
                additional = child.word
                break
        normal_form = analyzer.parse(morph_info.word)[0].normal_form
        normal_form2 = cut_affix(normal_form, morph=analyzer)
        if not isinstance(normal_form2, list):
            normal_form = normal_form2
        if normal_form in MOVE_VERBS:
            if 'обст' not in edge_types:
                questions.append(f'Откуда {morph_info.word} {additional}?' if additional else f'Откуда {morph_info.word}?')
                questions.append(f'Куда {morph_info.word} {additional}?' if additional else f'Куда {morph_info.word}?')
                questions.append(f'Как {morph_info.word} {additional}?' if additional else f'Как {morph_info.word}?')
                if 'past' in morph_info.tag:
                    questions.append('Когда это произошло?')
                elif {'futr', 'perf'} in morph_info.tag:
                    questions.append('Когда это произойдёт?')
            else:
                where_allowed = True
                for num, edge_type in enumerate(edge_types):
                    if edge_type == 'обст':
                        edge = vertex.out_edges()[num]
                        child = graph.vs[edge.target]
                        if 'ADVB' not in child['morph_info_list'][0].tag and child['morph_info_list'][
                            0] not in TIME_ADVERBS:
                            where_allowed = False
                if vertex['token'] in TIME_ADVERBS:
                    where_allowed = False
                if where_allowed:
                    questions.append(f'Откуда {morph_info.word} {additional}?' if additional else f'Откуда {morph_info.word}?')
                    questions.append(f'Куда {morph_info.word} {additional}?' if additional else f'Куда {morph_info.word}?')
                    questions.append(f'Как {morph_info.word} {additional}?' if additional else f'Как {morph_info.word}?')
                    if 'past' in morph_info.tag:
                        questions.append('Когда это произошло?')
                    elif {'futr', 'perf'} in morph_info.tag:
                        questions.append('Когда это произойдёт?')
        else:
            if 'обст' not in edge_types:
                questions.append(f'Где {morph_info.word} {additional}?' if additional else f'Где {morph_info.word}?')
                questions.append(f'Как {morph_info.word} {additional}?' if additional else f'Как {morph_info.word}?')
                if 'past' in morph_info.tag:
                    questions.append('Когда это произошло?')
                elif {'futr', 'perf'} in morph_info.tag:
                    questions.append('Когда это произойдёт?')
            else:
                how_allowed = True
                where_allowed = True
                for num, edge_type in enumerate(edge_types):
                    if edge_type == 'обст':
                        edge = vertex.out_edges()[num]
                        child = graph.vs[edge.target]
                        if 'ADVB' in child['morph_info_list'][0].tag:
                            how_allowed = False
                        else:
                            where_allowed = False
                if how_allowed:
                    questions.append(f'Как {morph_info.word} {additional}?' if additional else f'Как {morph_info.word}?')
                if where_allowed:
                    questions.append(f'Где {morph_info.word} {additional}?' if additional else f'Где {morph_info.word}?')
                    if 'past' in morph_info.tag:
                        questions.append('Когда это произошло?')
                    elif {'futr', 'perf'} in morph_info.tag:
                        questions.append('Когда это произойдёт?')

    questions = []
    for vertex in graph.vs:
        if not vertex['is_word']:
            continue
        morph_info: SentenceGraph.MorphInfo = vertex['morph_info_list'][0]
        edge_types = [edge['type'] for edge in vertex.out_edges()]

        if 'NOUN' in morph_info.tag:
            noun()
        elif morph_info.tag.POS in {'VERB', 'GRND', 'PRTF', 'PRTS'}:
            verb(vertex)
        elif 'NUMR' in morph_info.tag:
            if morph_info.word in {'двое', 'трое'} or morph_info.word[-1:] == 'о' and '1-компл' not in edge_types:
                questions.append(f'Кого {morph_info.word}')
    return questions


def main():
    analyzer = MorphAnalyzer()

    # sentence = input()
    # graph = SentenceGraph(sentence, analyzer=analyzer)
    number = 27
    graph = get_example_graph(number, analyzer=analyzer)

    for question in get_questions(graph, analyzer=analyzer,
                                  QuestionTypes=question_types(analyzer)):
        print(question)
    print('\n', graph['json'])
    show(graph)


if __name__ == '__main__':
    main()
