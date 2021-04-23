from math import log

from krasoteevo.examples import get_count, get_example_json
from krasoteevo.sentence_graph import SentenceGraph
from pymorphy2 import MorphAnalyzer


class QUESTION_TYPES:
    WHICH = 'какой'
    WHO = 'кто'
    HOW_MANY = 'сколько'
    WHERE = 'где'
    WHEN = 'когда'
    WHERE_FROM = 'откуда'
    WHERE_TO = 'куда'
    WHY = 'почему'


analyzer = MorphAnalyzer()


class Question:
    def __init__(self, question_type: str):
        self.question_type = question_type

# g = SentenceGraph('Качели с девочкой и мальчиком качаются', tag_class=analyzer.TagClass)


def print_questions(g: SentenceGraph):
    for vertex in g.vs:
        if vertex['is_word']:
            morph_info: SentenceGraph.MorphInfo = vertex['morph_info_list'][0]
            pos = morph_info.tags.POS
            edges = g.es.select(_source=vertex['id'])
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

# print_questions(g)

# print('\n', g['json'])
# show(g)


links = set()
entrance_counts = dict()
doc_numbers = dict()


for number in range(get_count()):
    print(number)
    json_obj = get_example_json(number)
    for obj in json_obj['synts']:
        link = obj[2]
        if link in links:
            entrance_counts[link] += 1
            doc_numbers[link].add(number)
        else:
            entrance_counts[link] = 1
            doc_numbers[link] = {number}
            links.add(link)

word_total_count = sum([entrance_counts[link] for link in links])
doc_total_count = get_count()
print(links)

for link in links:
    count = entrance_counts[link]
    tf = str(entrance_counts[link]/word_total_count)[:6]
    idf = str(log(doc_total_count/len(doc_numbers[link]) + 1e-20))[:6]
    tf_idf = str(entrance_counts[link]/word_total_count*log(doc_total_count/len(doc_numbers[link]) + 1e-20))[:6]
    print(f'{link:<15} COUNT: {count:<6} TF: {tf:<6} IDF: {idf:<6} TF-IDF: {tf_idf:<6}')
