import pytest
import requests
import json
from http_tests.http_helpers import register_user, create_dm, dm_message_send, channels_create, channel_invite, channel_join
from http_tests.fixtures import clear_data, user_reg, channel_set_up, dm_set_up
from src import config

def test_users(clear_data, user_reg):
    '''
    Test that users all returns a list of dictionaries of all the users in the system

    Parameters:
        None

    Returns:   
        List of dictionaries of the users in Dreams
    '''
    data = {'token' : user_reg.get('token')}
    resp = requests.get(config.url + 'users/all/v1', params=data)

    load = resp.json()
    assert len(load) == 1

def test_users_stats(clear_data, dm_set_up):
    '''
    Test that the dreams stats are successfully returned

    Parameters:
        channel_set_up(fixture)

    Returns:
        Dictionary with the dream stats
    '''


    data = {'token' : dm_set_up[0].get('token')}
    
    #send a message on that dm
    string = 'hello there world this is a test to test that this works'
    message_list = string.split()
    msgs = []
    for i in range(len(message_list)):
        msgs.append(dm_message_send(config.url + 'message/senddm/v1', dm_set_up[0].get('token'), dm_set_up[3].get('dm_id'), message_list[i]))

    #create an additional channel between all 3 users
    channel1 = channels_create(config.url + 'channels/create/v2', dm_set_up[0].get('token'), 'motherland', True)
    channel_invite(config.url + 'channel/invite/v2', dm_set_up[0].get('token'), channel1.get('channel_id'), dm_set_up[2].get('auth_user_id'))
    channel_join(config.url + 'channel/join/v2', dm_set_up[2].get('token'), channel1.get('channel_id'))

    resp = requests.get(config.url + 'users/stats/v1', params=data)

    load = resp.json()

    assert resp.status_code == 200
    assert load['dreams_stats'].get('channels_exist')[0].get('num_channels_exist') == 1
    assert load['dreams_stats'].get('dms_exist')[0].get('num_dms_exist') == 1
    assert load['dreams_stats'].get('messages_exist')[0].get('num_messages_exist') == 12
    assert load['dreams_stats'].get('utilization_rate') == 1.0
