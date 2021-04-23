"""Functions to load locally saved examples of SentenceGraphs"""

import json
import pathlib
import os

from krasoteevo.sentence_graph import SentenceGraph

_dir_path = pathlib.Path(__file__).parent.absolute() / 'examples_dir'


def get_count():
    """
    :return: return count of existing examples
    """
    return len([path for path in os.listdir(_dir_path) if path[-5:] == '.json'])


class FilenameException(Exception):
    pass


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
    except Exception as e:
        raise FilenameException(f"File {name} doesn't exists in examples") from e
    return json.load(file)


def get_example_graph(number: int, tag_class: type = None):
    """
    :param number: number of example. Starts from 0, upper bound is equal to `get_count() - 1`
    :return: SentenceGraph that is loaded from example with number `number`
    """
    json_obj = get_example_json(number)
    return SentenceGraph(json_obj, tag_class=tag_class)


def get_example_text(number: int):
    """
    :param number: number of example. Starts from 0, upper bound is equal to `get_count() - 1`
    :return: example with number `number` as a string
    """
    name = get_example_filename(number)
    try:
        file = open(_dir_path / name)
    except Exception as e:
        raise FilenameException(f"File {name} doesn't exists in examples") from e
    return file.read()
