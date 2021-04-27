"""Function to visualize SentenceGraph. Nothing serious but it's better than nothing"""

from igraph import plot, InternalError

from krasoteevo.sentence_graph import SentenceGraph

DEFAULT_VERTEX_COLOR = 'grey'
DEFAULT_EDGE_COLOR = 'black'

POS_TO_COLORS = {
    'NOUN': 'light blue',
    'CONJ': 'yellow',
    'VERB': 'red',
    'NPRO': 'blue',
    'PREP': 'green',
    'ADJF': 'magenta',
    'GRND': 'red',
    'ADVB': 'cyan',
    'PRTF': 'violet',
    None: DEFAULT_VERTEX_COLOR
}

LINK_TYPE_TO_COLORS = {
    # 'агент'
    # 'присвяз'
    # 'инф-союзн'
    # 'аппоз'
    # 'атриб'
    # 'об-аппоз'
    # 'инф-союзн'
    '1-компл': 'light blue',
    'обст': 'blue',
    'соч-союзн': 'yellow',
    'сочин': 'yellow',
    'предл': 'green',
    'предик': 'red',
    'опред': 'violet',
    'огранич': 'cyan',
    'несобст-агент': 'dark green'
}


def _pos(v):
    """
    :param v: vertex of SentenceGraph
    :return: POS of the first SentenceGraph.MorphInfo in v['morph_info_list'] or None
    """
    if not v['is_word']:
        return None
    morph_info: SentenceGraph.MorphInfo = v['morph_info_list'][0]
    return morph_info.raw_tag.split(',')[0]


def show(g: SentenceGraph):
    g.vs['label'] = g['json']['tokens']
    g.es['label'] = g.es['type']

    g.vs['color'] = [POS_TO_COLORS.get(_pos(v), DEFAULT_VERTEX_COLOR) for v in g.vs]
    g.es['color'] = [LINK_TYPE_TO_COLORS.get(e['type'], DEFAULT_EDGE_COLOR) for e in g.es]
    try:
        layout = g.layout_reingold_tilford()
    except InternalError:
        layout = g.layout_kamada_kawai()
    plot(g, layout=layout, margin=(40, 20, 40, 20), bbox=(1000, 600))
