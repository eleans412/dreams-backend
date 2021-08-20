import pytest
import requests
import json
from http_tests.http_helpers import register_user, create_dm
from http_tests.fixtures import clear_data, dm_set_up, message_dm_setup, channel_set_up, user_reg
from src import config


def test_dm_create(clear_data, channel_set_up):
    '''
    Test that a dm is successfully created

    Parameters:
        None
    
    Returns:
        Dictionary with dm_id and dm_name
    '''
    data = {
        'token' : channel_set_up[0].get('token'),
        'u_ids' : [channel_set_up[1].get('auth_user_id'), channel_set_up[2].get('auth_user_id')]
    }
    resp = requests.post(config.url + 'dm/create/v1', json= data)

    load = resp.json()

    assert load['dm_id'] == 1
    assert load['dm_name'] == 'emilyprentiss, jenniferjareau, penelopegarcia'

def test_create_user_invalid(clear_data, user_reg):
    '''
    Test that an input error is raised when u_id is not a valid user

    Parameters:
        None
    
    Returns:
        Inputerror
    '''
    data = {
        'token' : user_reg.get('token'),
        # Input an invalid user id to add to the dm
        'u_ids' : [32645]
    }
    resp = requests.post(config.url + 'dm/create/v1', json= data)

    assert resp.status_code == 400

def test_dm_remove(clear_data, dm_set_up):
    '''
    Test that a dm is successfully removed

    Parameters:
        None
    
    Returns:
        Empty Dictionary
    '''
    remove_data = {
        'token' : dm_set_up[0].get('token'),
        'dm_id' : dm_set_up[3].get('dm_id')
    }

    resp = requests.delete(config.url + 'dm/remove/v1', json=remove_data)

    assert resp.status_code == 200

def test_dm_invite(clear_data, dm_set_up):
    '''
    Test that a user is successfully added to dm

    Parameters:
        None
    
    Returns:
        Empty Dictionary
    '''
    user = register_user(config.url + 'auth/register/v2', 'ajmichalka@testemail.com', 'testpassworkdas14', 'andrea', 'michalka')

    invite_data = {
        'token' : dm_set_up[0].get('token'),
        'dm_id' : dm_set_up[3].get('dm_id'),
        'u_id' : user.get('auth_user_id')
    }

    resp = requests.post(config.url + 'dm/invite/v1', json=invite_data)

    assert resp.status_code == 200

def test_dm_messages(clear_data, message_dm_setup):
    '''
    Test that a dm messages within the range of start and start + 50 are returned

    Parameters:
        None
    
    Returns:
        Dictionary with dm_messages, start and end
    '''

    request_msg_data = {
        'token' : message_dm_setup[0].get('token'),
        'dm_id' : message_dm_setup[3].get('dm_id'),
        'start' : 0
    }

    resp = requests.get(config.url + 'dm/messages/v1', params=request_msg_data)
    load = resp.json()

    assert len(load['messages']) == 12
    assert load['start'] == 0
    assert load['end'] == -1
    assert load['messages'][0]['message'] == 'works'
    assert load['messages'][11]['message'] == 'hello'

def test_dm_leave(clear_data, dm_set_up):
    '''
    Test that a successfully leaves dm

    Parameters:
        None
    
    Returns:
        Dictionary with dm_id and dm_name
    '''
    
    leave_data = {
        'token' : dm_set_up[0].get('token'),
        'dm_id' : dm_set_up[3].get('dm_id')
    }

    resp = requests.post(config.url + 'dm/leave/v1', json=leave_data)

    assert resp.status_code == 200