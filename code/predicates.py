from pymorphy2 import MorphAnalyzer
from pymorphy2.units import KnownPrefixAnalyzer

from classes import ParseLike, ComplexVerb

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


def is_present(verb: ParseLike):
    return {'futr', 'impf'} in verb.tag or 'pres' in verb.tag


def is_move_verb(verb: ParseLike, analyzer: MorphAnalyzer):
    if isinstance(verb, ComplexVerb):
        return is_move_verb(verb.modal, analyzer) or is_move_verb(verb.infinitive, analyzer)
    normal_form = analyzer.parse(verb.word)[0].normal_form
    normal_form2 = cut_affix(normal_form, morph=analyzer)
    if not isinstance(normal_form2, list):
        normal_form = normal_form2
    return normal_form in MOVE_VERBS


def is_feeling_verb(verb: ParseLike, analyzer: MorphAnalyzer):
    if isinstance(verb, ComplexVerb):
        return is_feeling_verb(verb.modal, analyzer) or is_feeling_verb(verb.infinitive, analyzer)
    normal_form = analyzer.parse(verb.word)[0].normal_form
    normal_form2 = cut_affix(normal_form, morph=analyzer)
    if not isinstance(normal_form2, list):
        normal_form = normal_form2
    return normal_form in FEELING_VERBS


_russian_prefixes = (
    'без', 'бес', 'в', 'вз', 'взо', 'вне', 'внутри', 'во', 'воз', 'возо', 'вос', 'вс', 'вы', 'до',
    'еже', 'за', 'зако', 'из', 'изо', 'ис', 'испод', 'к', 'кое', 'меж', 'междо', 'между', 'на',
    'над', 'надо', 'наи', 'не', 'недо', 'ни', 'низ', 'низо', 'нис', 'о', 'об', 'обез', 'обес',
    'обо', 'около', 'от', 'ото', 'па', 'пере', 'по', 'под', 'подо', 'поза', 'после', 'пра', 'пре',
    'пред', 'преди', 'предо', 'при', 'про', 'противо', 'раз', 'разо', 'рас', 'роз', 'рос', 'с',
    'сверх', 'со', 'среди', 'су', 'тре', 'у', 'через', 'черес', 'чрез', 'чрес')
_russian_postfixes = ('ся', 'сь')


def cut_affix(word: str, prefixes=_russian_prefixes, suffixes=_russian_postfixes, morph=MorphAnalyzer()):
    """Function to remove prefixes and postfixes from Russian words"""
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
