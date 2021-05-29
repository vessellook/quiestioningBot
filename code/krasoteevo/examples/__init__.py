"""Functions to load locally saved examples of SentenceGraphs"""

import json
import pathlib
import os
import re

import pymorphy2

from krasoteevo.sentence_graph import SentenceGraph
from krasoteevo.request import (
    request_syntax_analysis,
    TooLongSentenceException,
    EmptySentenceException)


__all__ = [
    'get_count',
    'get_example_filename',
    'get_example_json',
    'get_example_graph',
    'get_example_text',
    'update_examples'
]


_dir_path = pathlib.Path(__file__).parent.absolute()

filename_pattern = re.compile(r'^(0|[1-9][0-9]*)\.json$')
filename_format = '{}.json'


def get_count():
    """
    :return: return count of existing examples
    """
    return len(list(filter(filename_pattern.match, os.listdir(_dir_path))))


def get_example_filename(number: int):
    """
    :param number: number of example. Starts from 0, upper bound is equal to `get_count() - 1`
    :return: name of file in JSON format
    """
    return filename_format.format(number)


def get_example_json(number: int):
    """
    :param number: number of example. Starts from 0, upper bound is equal to `get_count() - 1`
    :return: JSON object that is loaded from example with number `number`
    """
    name = get_example_filename(number)
    with open(_dir_path / name) as file:
        return json.load(file)


def get_example_graph(number: int, analyzer: pymorphy2.MorphAnalyzer = None):
    """
    :param analyzer: it is pymorphy2.MorphAnlyzer class passed from pymorphy2
        It uses big dict (~15 GB) so the object of such class should be created one time
    :param number: number of example. Starts from 0, upper bound is equal to `get_count() - 1`
    :return: SentenceGraph that is loaded from example with number `number`
    """
    json_obj = get_example_json(number)
    return SentenceGraph(json_obj, analyzer=analyzer)


def get_example_text(number: int):
    """
    :param number: number of example. Starts from 0, upper bound is equal to `get_count() - 1`
    :return: example with number `number` as a string
    """
    name = get_example_filename(number)
    with open(_dir_path / name) as file:
        return file.read()


def _load(sentence: str, file_index: int):
    try:
        response = request_syntax_analysis(sentence)
    except (TooLongSentenceException, EmptySentenceException):
        return False
    text = response.text
    
    try:
        json_new = json.loads(text)
    except json.JSONDecodeError:
        return False

    correct = all(item in json_new for item in {'sentence', 'tokens', 'morphs', 'synts'})
    if not correct:
        return False
    path = _dir_path / get_example_filename(file_index)
    with open(path, 'w') as file:
        file.write(text)
    return True
    

def update_examples(new_sentences: list = None, only_new: bool = True):
    """Function to reload existing examples and add new examples"""
    count = get_count()
    fails_new = []
    fails_old = []
    if new_sentences is not None:
        file_index = count
        print('Start to load new sentences')
        for sentence_index, sentence in new_sentences:
            if _load(sentence, file_index):
                file_index += 1
                print(f'{get_example_filename(file_index)} created')
            else:
                print('Sentence with index', sentence_index, 'did not load')
                fails_new.append(sentence_index)
    if not only_new:
        print('Start to reload old sentences')
        for file_index in range(count):
            with open(_dir_path / get_example_filename(file_index)) as file:
                json_old = json.load(file)
            sentence = json_old['sentence']
            if _load(sentence, file_index):
                print(f'{get_example_filename(file_index)} reloading succeed')
            else:
                print(f'{get_example_filename(file_index)} reloading failed')
                fails_old.append(file_index)

    if fails_new:
        print('Fails in new sentences:', fails_new)
    if fails_old:
        print('Reloading of the following files failed:', fails_old)
