import pytest
import requests
import json
from http_tests.http_helpers import register_user
from http_tests.fixtures import clear_data, user_reg, channel_set_up
from src import config

def test_channels_create(clear_data, user_reg):
    '''
    Test that channels create successfully creates a channel

    Parameters:
        token (str) : the user calling the function
        name (str): name of the channel
        is_public (bool) : whether the channel is public or private

    Returns:
        Dictionary with channel_id
    '''
    resp = requests.post(config.url + 'channels/create/v2', json={'token': user_reg.get('token'), 'name' : 'motherland', 'is_public' : True})
    assert resp.status_code == 200

    load = resp.json()
    assert load['channel_id'] == 1

def test_channel_invalid_name(clear_data, user_reg):
    '''
    Test that input error is raised when name is more than 20 characters

    Parameters:
        token (str) : the user calling the function
        name (str): name of the channel
        is_public (bool) : whether the channel is public or private

    Returns:
        Dictionary with channel_id
    '''

    data = {'token': user_reg.get('token'), 'name' : 'motherlandisashowaboutwitchesandthesupernaturalandidontknowwhyimwatchingit', 'is_public' : True}
    resp = requests.post(config.url + 'channels/create/v2', json=data)

    assert resp.status_code == 400

def test_channels_list(clear_data, channel_set_up):
    '''
    Test that channels list successfully returns list of channels the user is a part of

    Parameters:
        token (str) : the user calling the function

    Returns:
        Dictionary with channels the user is part of 
    '''
    # Check how many users user3 in the fixture has joined
    data = {'token': channel_set_up[2].get('token')}
    resp = requests.get(config.url + 'channels/listall/v2', params=data)

    assert resp.status_code == 200

    load = resp.json()
    assert len(load['channels']) == 2

def test_channels_listall(clear_data, channel_set_up):
    '''
    Test that all channels are listed 

    Parameters:
        token (str) : the user calling the function

    Returns:
        Dictionary with all existing channels
    '''
    data = {'token': channel_set_up[0].get('token')}
    resp = requests.get(config.url + 'channels/listall/v2', params=data)
    assert resp.status_code == 200

    load = resp.json()
    assert len(load['channels']) == 2