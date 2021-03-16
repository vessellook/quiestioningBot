"""Tests for krasoteevo.request module"""
import pytest_cases

from krasoteevo.request import request_syntax_analysis


@pytest_cases.parametrize_with_cases(['sentence', 'expected'], cases='krasoteevo.tests.cases')
def test_syntax_analysis_request(sentence, expected):
    """Test function 'request' in module 'krasoteevo.request'"""
    response = request_syntax_analysis(sentence)
    assert expected == response.json()
