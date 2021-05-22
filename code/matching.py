from igraph import Vertex


class Node:
    def __init__(self, *, grammemes=None, white_list=None, black_list=None):
        if isinstance(grammemes, str):
            grammemes = tuple(grammemes)
        if isinstance(white_list, str):
            white_list = tuple(white_list)
        if isinstance(black_list, str):
            black_list = tuple(black_list)
        self.grammemes = grammemes
        self.white_list = white_list
        self.black_list = black_list
        self._children: list['Node'] = []

    def children(self, *children):
        self._children = children

    def match(self, vertex: Vertex):
        if not vertex['morph_inf_list']:
            return False
        if self.grammemes and self.grammemes not in vertex['morph_info_list'][0].tag:
            return False
        if self.white_list and vertex['morph_info_list'].normal_form.lower() not in self.white_list:
            return False
        if self.black_list and vertex['morph_info_list'].normal_form.lower() in self.black_list:
            return False
        if not self._children:
            return True
        children = {e.graph.vs[e.target] for e in vertex.out_edges()}
        for child_pattern in self._children:
            for child in filter(child_pattern.match, children):
                children.discard(child)
                break
            else:
                return False
        return True
