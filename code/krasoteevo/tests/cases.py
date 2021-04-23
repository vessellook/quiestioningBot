"""Test cases for test_request.py"""
import json
import pathlib

_dir_path = pathlib.Path(__file__).parent.absolute()


def case_sentence_1():
    sentence = "Школьник высадил полностью заряженный гаджет," \
               " потратив на игры и учёбу одинаковое время."
    json_str = open(f'{_dir_path}/data/0.json').read()
    return sentence, json.loads(json_str)


def case_sentence_2():
    sentence = 'Маша и Петя любили зверей, и мама отвела их в зоопарк.'
    json_str = open(f'{_dir_path}/data/1.json').read()
    return sentence, json.loads(json_str)


def case_sentence_3():
    sentence = 'Ваня идёт гулять.'
    json_str = open(f'{_dir_path}/data/2.json').read()
    return sentence, json.loads(json_str)
