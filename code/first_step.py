from enum import Enum

from igraph._igraph import Vertex
from pymorphy2 import MorphAnalyzer
from pymorphy2.analyzer import Parse

from krasoteevo.visualization import show
from krasoteevo.examples import get_example_graph
from krasoteevo.sentence_graph import SentenceGraph
from krasoteevo.tools import cut_affix, choose_parse


class QuestionTypes(Enum):
    WHICH = {'word': 'какой', 'tag': 'ADJF,Apro masc,sing,nomn'}
    WHO = {'word': 'кто', 'tag': 'NPRO,masc sing,nomn'}
    HOW_MANY = {'word': 'сколько', 'tag': 'ADVB'}
    WHERE = {'word': 'где', 'tag': 'ADVB,Ques'}
    WHEN = {'word': 'когда', 'tag': 'ADVB,Ques'}
    WHERE_FROM = {'word': 'откуда', 'tag': 'ADVB,Ques'}
    WHERE_TO = {'word': 'куда', 'tag': 'ADVB,Ques'}
    WHY = {'word': 'почему', 'tag': 'ADVB,Ques'}

    def __init__(self, value):
        self._value_ = value['word']
        self.word = value['word']
        self.raw_tag = value['tag']
        self.normal_form = value['normal_form'] if 'normal_form' in value else value['word']
        self._parse = None

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
            item._parse = choose_parse(word=item.word, tag=item.raw_tag, normal_form=item.normal_form,
                                       analyzer=analyzer)


class Question:
    def __init__(self, question_type: QuestionTypes, target_word: Parse, target_vertex: Vertex):
        self.question_type = question_type
        self.target_parse = target_word

    def __str__(self):
        if self.question_type is QuestionTypes.WHICH:
            if {'NOUN', 'plur'} in self.target_parse.tag:
                word = self.target_parse.inflect({'nomn'})
                return f'{QuestionTypes.WHICH.word.capitalize()} {word.word}?'
            elif {'NOUN'} in self.target_parse.tag:
                gender = self.target_parse.tag.gender if self.target_parse.tag.gender is not None else 'masc'
                which = QuestionTypes.WHICH.inflect({gender})
                word = self.target_parse.inflect({'nomn'})
                return f'{which.word.capitalize()} {word.word}?'
            else:
                raise Warning('Unreachable point')
        elif self.question_type is QuestionTypes.HOW_MANY:
            if 'NOUN' in self.target_parse.tag:
                word = self.target_parse.inflect({'gent'})
                return f'{QuestionTypes.HOW_MANY.word.capitalize()} {word.word}?'
        elif self.question_type is QuestionTypes.WHERE_FROM:
            if 'VERB' in self.target_parse.tag:
                return f'{QuestionTypes.WHERE_FROM.word} {self.target_parse.word}?'
        elif self.question_type is QuestionTypes.WHERE_TO:
            if 'VERB' in self.target_parse.tag:
                return f'{QuestionTypes.WHERE_TO.word} {self.target_parse.word}?'
        elif self.question_type is QuestionTypes.WHERE:
            if 'VERB' in self.target_parse.tag:
                return f'{QuestionTypes.WHERE.word} {self.target_parse.word}?'
        elif self.question_type is QuestionTypes.HOW:
            if 'VERB' in self.target_parse.tag:
                return f'{QuestionTypes.HOW.word} {self.target_parse.word}?'
        elif self.question_type is QuestionTypes.WHEN:
            if 'VERB' in self.target_parse.tag:
                if {'past', 'impf'} in self.target_parse.tag:
                    return f'Когда это происходило?'
                elif {'past', 'perf'} in self.target_parse.tag:
                    return f'Когда это произошло?'
                elif {'futr', 'perf'} in self.target_parse.tag:
                    return f'Когда это произойдёт?'
        elif self.question_type is QuestionTypes.WHO:
            if 'NUMR' in self.target_parse.tag:
                return f'{QuestionTypes.WHO.inflect("gent").word} {self.target_parse.word}?'


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


def get_questions(graph: SentenceGraph, analyzer: MorphAnalyzer):
    def noun():
        word = analyzer.parse(morph_info.word)[0]
        questions.append(Question(QuestionTypes.WHICH, word, vertex))

        if morph_info.tag.number == 'plur' and 'количест' not in edge_types:
            questions.append(Question(QuestionTypes.HOW_MANY, word, vertex))

    def verb(vertex):
        word = morph_info.parse
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
                questions.append(Question(QuestionTypes.WHERE_FROM, word, vertex))
                questions.append(Question(QuestionTypes.WHERE_TO, word, vertex))
                questions.append(Question(QuestionTypes.HOW, word, vertex))
                if {'futr', 'impf'} not in morph_info.tag:
                    questions.append(Question(QuestionTypes.WHEN, word, vertex))
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
                    questions.append(Question(QuestionTypes.WHERE_FROM, word, vertex))
                    questions.append(Question(QuestionTypes.WHERE_TO, word, vertex))
                    questions.append(Question(QuestionTypes.HOW, word, vertex))
                    if {'futr', 'impf'} not in morph_info.tag:
                        questions.append(Question(QuestionTypes.WHEN, word, vertex))
        else:
            if 'обст' not in edge_types:
                questions.append(Question(QuestionTypes.WHERE, word, vertex))
                questions.append(Question(QuestionTypes.HOW, word, vertex))
                if {'futr', 'impf'} not in morph_info.tag:
                    questions.append(Question(QuestionTypes.WHEN, word, vertex))
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
                    questions.append(Question(QuestionTypes.HOW, word, vertex))
                if where_allowed:
                    questions.append(Question(QuestionTypes.WHERE, word, vertex))
                    if {'futr', 'impf'} not in morph_info.tag:
                        questions.append(Question(QuestionTypes.WHEN, word, vertex))

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
                questions.append(Question(QuestionTypes.WHO, morph_info.parse, vertex))
    return questions


def main():
    analyzer = MorphAnalyzer()
    QuestionTypes.init(analyzer)

    # sentence = input()
    # graph = SentenceGraph(sentence, analyzer=analyzer)
    number = 27
    graph = get_example_graph(number, analyzer=analyzer)

    for question in get_questions(graph, analyzer=analyzer):
        print(question)
    print('\n', graph['json'])
    # show(graph)


if __name__ == '__main__':
    main()
