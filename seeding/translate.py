#!/usr/bin/env python3

import requests


def translate(input_text: str, model='en-cs', src='en', tgt='cs'):
    """
    Translates given text from a given source language to a given target language, using a REST API call to LINDAT
    Translation service with specified model.
    :param input_text: The text to be translated.
    :param model: The name of the translation model to be used.
    :param src: Source language identifier.
    :param tgt: Target language identifier.
    :return: The translated text.
    """
    url = f'https://lindat.mff.cuni.cz/services/translation/api/v2/models/{model}'

    payload = {
        'input_text': input_text,
        'src': src,
        'tgt': tgt
    }

    params = {
        'src': src,
        'tgt': tgt
    }

    response = requests.post(url, data=payload, params=params)

    response.encoding = 'utf-8'

    # Check for successful response
    if response.status_code == 200:
        return response.text.strip()
    else:
        return f"Error: {response.status_code}, {response.text}"
