import pytest
import requests
import json
from http_tests.http_helpers import register_user, channels_create
from http_tests.fixtures import clear_data, message_chan_setup
from src import config


def test_clear(message_chan_setup):
    '''
    Test that the clear wrapper removes all the data that has been set up

    Parameters:
        None

    Returns:
        Empty Dictionary
    '''
    resp = requests.delete(config.url + 'clear/v1')

    load = resp.json()

    assert load == {}

def test_search(clear_data, message_chan_setup):
    '''
    Test that the search function returns the messages that match the query string

    Paremeters:
        token (str): the user that is searching
        query_str (str) : the message being searched for

    Returns:
        Dictionary of messages that match the query string
    '''
    data = {
        'token' : message_chan_setup[0].get('token'),
        'query_str' : 'test',
    }
    resp = requests.get(config.url + 'search/v2', params=data)

    assert resp.status_code == 200

    load = resp.json()
    assert len(load['messages']) == 2
