"""Function to visualize SentenceGraph. Nothing serious but it's better than nothing"""

import random

from igraph import plot, InternalError

from krasoteevo.sentence_graph import SentenceGraph

DEFAULT_VERTEX_COLOR = 'grey'
DEFAULT_EDGE_COLOR = 'black'

COLORS = (
    'dark orange', 'dark red', 'indigo', 'green', 'magenta', 'cyan', 'black', 'yellow green',
    'maroon'
)

POS_TO_COLORS = {
    'VERB': 'green',  # глагол
    'GRND': 'green',  # деепричастие
    'PRTF': 'green',  # полное причастие
    'PRTS': 'green',  # краткое причастие
    'INFN': 'green',  # инфинитив. Пример: сделать
    'COMP': 'green',  # компаратив. Пример: круче
    'ADVB': 'yellow',  # наречие
    'NOUN': 'red',  # существительное
    'NPRO': 'red',  # местоимение-существительное
    'ADJF': 'light pink',  # полное прилагательное
    'ADJS': 'light pink',  # краткое прилагательное
    'NUMR': 'blue',  # числительное
    'NUMB': 'blue',  # число. Пример: 100
    'PRED': 'cyan',  # предикатив. Пример: некогда
    'PREP': 'cyan',  # предлог
    'CONJ': 'cyan',  # союз
    'PRCL': 'grey',  # частица
    None: DEFAULT_VERTEX_COLOR
}


def _pos(vertex):
    """
    :param v: vertex of SentenceGraph
    :return: POS of the first SentenceGraph.MorphInfo in v['morph_info_list'] or None
    """
    if not vertex['is_word']:
        return None
    morph_info: SentenceGraph.MorphInfo = vertex['morph_info_list'][0]
    return morph_info.raw_tag.split(',')[0]


def show(graph: SentenceGraph):
    """Show colorful plot with SentenceGraph"""
    def double(iterable):
        return iterable, iterable

    copy: SentenceGraph = graph.copy()
    copy.simplify(loops=False, combine_edges={'type': ', '.join})
    copy.vs['label'] = [f"{v['token']} [{len(v['morph_info_list'])}]" if v['is_word']
            else v['token'] for v in copy.vs]
    copy.es['label'] = copy.es['type']

    copy.vs['color'] = [POS_TO_COLORS.get(_pos(v), DEFAULT_VERTEX_COLOR) for v in copy.vs]
    copy.es['color'], copy.es['label_color'] = double(random.choices(COLORS, k=len(copy.es)))
    try:
        layout = copy.layout_reingold_tilford()
    except InternalError:
        layout = copy.layout_kamada_kawai()
    plot(copy, layout=layout, margin=(40, 20, 40, 20), bbox=(1200, 600))
