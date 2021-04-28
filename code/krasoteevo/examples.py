"""Functions to load locally saved examples of SentenceGraphs"""

import json
import pathlib
import os

import pymorphy2

from krasoteevo.sentence_graph import SentenceGraph
from krasoteevo.request import (
    request_syntax_analysis,
    TooLongSentenceException,
    EmptySentenceException)

_dir_path = pathlib.Path(__file__).parent.absolute() / 'examples_dir'


def get_count():
    """
    :return: return count of existing examples
    """
    return len([path for path in os.listdir(_dir_path) if path[-5:] == '.json'])


def get_example_filename(number: int):
    """
    :param number: number of example. Starts from 0, upper bound is equal to `get_count() - 1`
    :return: name of file in JSON format
    """
    return f'{number}.json'


def get_example_json(number: int):
    """
    :param number: number of example. Starts from 0, upper bound is equal to `get_count() - 1`
    :return: JSON object that is loaded from example with number `number`
    """
    name = get_example_filename(number)
    try:
        file = open(_dir_path / name)
    except FileNotFoundError as err:
        raise FileNotFoundError(f"File {name} for example number {number} "
                                 "doesn't exists in examples") from err
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
    try:
        file = open(_dir_path / name)
    except FileNotFoundError as err:
        raise FileNotFoundError(f"File {name} for example number {number} "
                                         "doesn't exists in examples") from err
    return file.read()


def _load(sentence: str, file_index: int):
    try:
        response = request_syntax_analysis(sentence)
    except (TooLongSentenceException, EmptySentenceException):
        return False
    text = response.text
    json_new = json.loads(text)
    correct = all((item in json_new for item in {'sentence', 'tokens', 'morphs', 'synts'}))
    if correct:
        file = open(_dir_path / get_example_filename(file_index), 'w')
        file.write(text)
        file.close()
        return True
    return False


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
            json_old = json.load(_dir_path / get_example_filename(file_index))
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
