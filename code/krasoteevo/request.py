"""Function to send request to service to parse sentence"""

import requests


def request_syntax_analysis(sentence: str) -> requests.Response:
    """
    Send request to the service to parse Russian sentence

    :param sentence: the Russian sentence you want to parse

    :raises Exception: empty sentence is not allowed
    :raises Exception: sentence with more than 300 characters is not allowed, because it breaks the
     service

    :return: the requests.Response object with syntax analysis result data in JSON format
    """
    if len(sentence) == 0:
        raise Exception('Empty sentence')
    if len(sentence) > 300:
        raise Exception('Too big sentence')
    params = {'format': 'json', 'text': sentence}
    response = requests.get("https://krasoteevo.ru/syntax", params=params,
                            verify=False  # don't verify SSL certificate
                            )
    return response
