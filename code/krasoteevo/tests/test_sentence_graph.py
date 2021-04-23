"""Tests for krasoteevo.sentence_graph module"""
import pytest_cases
import pytest

from krasoteevo.sentence_graph import SentenceGraph


@pytest_cases.parametrize_with_cases(['sentence', 'expected_json_obj'],
                                     cases='krasoteevo.tests.cases')
def test_json_by_sentence(sentence, expected_json_obj):
    """Tests for SentenceGraph construction from sentence string"""
    graph = SentenceGraph(sentence)
    assert graph['sentence'] == sentence
    assert graph['json'] == expected_json_obj


@pytest_cases.parametrize_with_cases(['sentence', 'json_obj'], cases='krasoteevo.tests.cases')
def test_json(sentence, json_obj):
    graph = SentenceGraph(json_obj)
    assert graph['sentence'] == sentence
    assert graph['json'] == json_obj

#
# @pytest_cases.parametrize_with_cases(['sentence', 'expected_json_obj'],
#                                      cases='krasoteevo.tests.cases')
# def test_morph_info_lists(sentence, expected_json_obj):
#     """Tests for SentenceGraph construction from sentence string"""
#     graph = SentenceGraph(sentence)
#     for vertex in graph.vs:
#     assert graph['sentence'] == sentence
#     assert graph['json'] == expected_json_obj
