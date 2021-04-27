from pymorphy2 import MorphAnalyzer
from pymorphy2.units.by_analogy import KnownPrefixAnalyzer

_russian_prefixes = (
    'без', 'бес', 'в', 'вз', 'взо', 'вне', 'внутри', 'во', 'воз', 'возо', 'вос', 'вс', 'вы', 'до',
    'еже', 'за', 'зако', 'из', 'изо', 'ис', 'испод', 'к', 'кое', 'меж', 'междо', 'между', 'на',
    'над', 'надо', 'наи', 'не', 'недо', 'ни', 'низ', 'низо', 'нис', 'о', 'об', 'обез', 'обес',
    'обо', 'около', 'от', 'ото', 'па', 'пере', 'по', 'под', 'подо', 'поза', 'после', 'пра', 'пре',
    'пред', 'преди', 'предо', 'при', 'про', 'противо', 'раз', 'разо', 'рас', 'роз', 'рос', 'с',
    'сверх', 'со', 'среди', 'су', 'тре', 'у', 'через', 'черес', 'чрез', 'чрес')

_russian_postfixes = ('ся', 'сь')


def cut_affix(word, prefixes=_russian_prefixes, suffixes=_russian_postfixes, morph=MorphAnalyzer()):
    if word[-2:] in suffixes:
        word = word[:-2]
    analyzer = KnownPrefixAnalyzer(prefixes)
    analyzer.init(morph)
    seen = set()
    word_lower = word.lower()
    parsed = analyzer.parse(word, word_lower, seen)
    if not parsed:
        return word
    tmp = parsed[0]
    # print(parsed)  # debug
    # print(tmp)  # debug
    # print(seen)  # debug
    if len(tmp) >= 5:
        if tmp[4] and tmp[4][0]:
            return morph.normal_forms(tmp[4][0][1])[0]
    return tmp