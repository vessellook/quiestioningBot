"""Function to visualize SentenceGraph. Nothing serious but it's better than nothing"""

from igraph import plot, InternalError


from krasoteevo.sentence_graph import SentenceGraph


POS_TO_COLORS = {
    'NOUN': 'light blue',
    'CONJ': 'yellow',
    'VERB': 'red',
    'NPRO': 'blue',
    'PREP': 'green',
    'ADJF': 'magenta',
    'GRND': 'red',
    'ADVB': 'cyan',
    'PRTF': 'violet'
}

LINK_TYPE_TO_COLORS = {
    #'агент'
    #'присвяз'
    #'инф-союзн'
    #'аппоз'
    #'атриб'
    #'об-аппоз'
    #'инф-союзн'
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


def show(g: SentenceGraph):
    g.vs['label'] = g['json']['tokens']
    g.vs['color'] = [
        POS_TO_COLORS.get(v['morph_info_list'][0].raw_tags.split(',')[0], 'grey') if v['is_word'] else 'grey' for v in
        g.vs]
    g.es['label'] = g.es['type']
    g.es['color'] = [LINK_TYPE_TO_COLORS.get(e['type'], 'black') for e in g.es]
    try:
        layout = g.layout_reingold_tilford()
    except InternalError:
        layout = g.layout_kamada_kawai()
    plot(g, layout=layout, margin=(40, 20, 40, 20), bbox=(1000, 600))