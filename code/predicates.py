from igraph import Vertex
from pymorphy2 import MorphAnalyzer

from parse_proxy.complex_verb import ComplexVerb
from parse_proxy import ParseProxy
from matching import Node

MOVE_VERBS = (
    'бегать', 'бежать', 'брести', 'бродить', 'везти', 'вести', 'водить', 'возить', 'гнать',
    'гнаться', 'гонять', 'гоняться', 'ездить', 'ехать', 'идти', 'йти', 'катать', 'кататься',
    'катить', 'катиться', 'лазать', 'лазить', 'лезть', 'летать', 'лететь', 'нести', 'нестись',
    'носить', 'носиться', 'плавать', 'плыть', 'ползать', 'ползти', 'таскать', 'тащить', 'ходить')

FEELING_VERBS = (
    'блаженствовать', 'боготворить', 'бояться', 'брезговать', 'веселиться', 'взбудоражиться',
    'взволновать', 'влюблять', 'возбуждаться', 'возмущать', 'возненавидеть', 'восторгаться',
    'восхищаться', 'восхищаться', 'всполошиться', 'гневить', 'горевать', 'грустить', 'дивиться',
    'докучать', 'досадовать', 'досаждать', 'жалеть', 'загореться', 'злить', 'злиться',
    'злорадствовать', 'изводить', 'измучиться', 'изнемогать', 'изнывать', 'изумляться',
    'интересоваться', 'испугаться', 'конфузить', 'конфузиться', 'кручиниться', 'ласкать',
    'ликовать', 'любить', 'любоваться', 'маяться', 'млеть', 'мущаться', 'невзлюбить',
    'недолюбливать', 'недоумевать', 'нежить', 'ненавидеть', 'нервничать', 'нравиться',
    'оберегать', 'обидеться', 'обижаться', 'обнимать', 'ободриться', 'обожать', 'обозлиться',
    'огорчать', 'огорчаться', 'ожесточить', 'оживиться', 'озлобить', 'омрачать', 'опасаться',
    'опечалить', 'опечалиться', 'опешить', 'опротиветь', 'осмелеть', 'осмелиться', 'остерегаться',
    'осудить', 'оторопеть', 'очаровать', 'очароваться', 'переживать', 'печалить', 'печалиться',
    'пленять', 'повеселеть', 'покорять', 'поразиться', 'почитать', 'презирать', 'приголубить',
    'пугаться', 'радоваться', 'развеяться', 'раздражать', 'разъяриться', 'располагать',
    'рассвирепеть', 'рассердиться', 'расстроить', 'расстроиться', 'расхрабриться', 'расшевелиться',
    'робеть', 'сердить', 'сердиться', 'сетовать', 'сжалиться', 'симпатизировать', 'скучать',
    'смелеть', 'смущать', 'соболезновать', 'сожалеть', 'сокрушаться', 'сопереживать', 'сострадать',
    'сочувствовать', 'стесняться', 'страдать', 'стыдиться', 'терзаться', 'томить', 'томиться',
    'торжествовать', 'тосковать', 'трепетать', 'трусить', 'тушеваться', 'тяготиться', 'уважать',
    'увлекаться', 'удивляться', 'удручать', 'унижать', 'усовестить', 'успокоиться', 'устыдить',
    'устыдиться', 'утешиться', 'уязвить', 'хандрить', 'чествовать', 'чтить')

MONTHS = ('январь', 'февраль', 'март', 'апрель', 'май', 'июнь', 'июль', 'август', 'сентябрь',
          'октябрь', 'ноябрь', 'декабрь')

TIME_UNITS = ('секунда', 'минута', 'час', 'день', 'неделя', 'декада', 'месяц', 'год', 'десятилетие',
              'столетие', 'век', 'тысячелетие')


def is_present(verb: ParseProxy):
    return {'futr', 'impf'} in verb.tag or 'pres' in verb.tag


def is_move_verb(verb: ParseProxy, analyzer: MorphAnalyzer):
    if isinstance(verb, ComplexVerb):
        return is_move_verb(verb.modal, analyzer) or is_move_verb(verb.infinitive, analyzer)
    normal_form_cleared = cut_affix(verb.normal_form, analyzer=analyzer)
    if isinstance(normal_form_cleared, str):
        return normal_form_cleared in MOVE_VERBS
    return verb.normal_form in MOVE_VERBS


def is_feeling_verb(verb: ParseProxy, analyzer: MorphAnalyzer):
    if isinstance(verb, ComplexVerb):
        return is_feeling_verb(verb.modal, analyzer) or is_feeling_verb(verb.infinitive, analyzer)
    normal_form = verb.normal_form
    normal_form2 = cut_affix(verb.normal_form, analyzer=analyzer)
    if not isinstance(normal_form2, list):
        normal_form = normal_form2
    return normal_form in FEELING_VERBS


def is_time_construction(vertex: Vertex):
    def match(pattern):
        return pattern.match(vertex)

    pattern1 = Node(grammemes='PREP', white_list=('в', 'на')).children(
        Node(white_list=TIME_UNITS).children(
            Node(white_list=('следующий', 'текущий', 'прошлый', 'прошедший', 'этот')))
    )

    pattern2 = Node(grammemes='PREP', white_list=('к', 'ко')).children(
        Node(grammemes='NUMR'),
        Node(white_list=TIME_UNITS)
    )

    pattern3 = Node(grammemes='PREP', white_list='за').children(
        Node(white_list=TIME_UNITS)
    )

    pattern4 = Node(grammemes='PREP', white_list='перед').children(
        Node(white_list=('сон', 'ужин', 'обед', 'ужин'))
    )

    pattern5 = Node(grammemes='PREP', white_list='до').children(
        Node(white_list='наш'),
        Node(white_list='эра')
    )
    return any(map(match, [pattern1, pattern2, pattern3, pattern4, pattern5]))


_russian_prefixes = (
    'без', 'бес', 'в', 'вз', 'взо', 'вне', 'внутри', 'во', 'воз', 'возо', 'вос', 'вс', 'вы', 'до',
    'еже', 'за', 'зако', 'из', 'изо', 'ис', 'испод', 'к', 'кое', 'меж', 'междо', 'между', 'на',
    'над', 'надо', 'наи', 'не', 'недо', 'ни', 'низ', 'низо', 'нис', 'о', 'об', 'обез', 'обес',
    'обо', 'около', 'от', 'ото', 'па', 'пере', 'по', 'под', 'подо', 'поза', 'после', 'пра', 'пре',
    'пред', 'преди', 'предо', 'при', 'про', 'противо', 'раз', 'разо', 'рас', 'роз', 'рос', 'с',
    'сверх', 'со', 'среди', 'су', 'тре', 'у', 'через', 'черес', 'чрез', 'чрес')
_russian_postfixes = ('ся', 'сь')


class NoPrefixToRemoveException(Exception):
    pass


def _remove_prefix(word, prefixes, analyzer):
    for prefix in prefixes:
        if word.startswith(prefix):
            new_word = word[len(prefix):]
            if analyzer.word_is_known(new_word):
                return new_word
    raise NoPrefixToRemoveException


def cut_affix(word: str, *, analyzer: MorphAnalyzer, prefixes=_russian_prefixes,
              suffixes=_russian_postfixes):
    """Function to remove prefixes and postfixes from Russian words"""
    for suffix in suffixes:
        if word.endswith(suffix):
            word = word[:-len(suffix)]
    try:
        while True:
            word = _remove_prefix(word, prefixes, analyzer)
    except NoPrefixToRemoveException:
        return word
