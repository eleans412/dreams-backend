import pytest
import requests
import json
from http_tests.http_helpers import register_user, channels_create, channel_invite
from http_tests.fixtures import clear_data, channel_set_up, message_chan_setup
from src import config


def test_invite_success(clear_data, channel_set_up):
    '''
    Test that an invite is successful

    Parameters:
        None

    Returns:
        Empty dictionary
    '''
    # Generate a user to add
    user = register_user(config.url + 'auth/register/v2', 'shelbygoodkind@testemail.com', 'testpassworkdas14', 'shelby', 'goodkind')
    data = {
        'token' : channel_set_up[0].get('token'), 
        'channel_id' : channel_set_up[3].get('channel_id'), 
        'u_id' : user.get('auth_user_id'),
        }

    resp = requests.post(config.url + 'channel/invite/v2', json=data)
    assert resp.status_code == 200

    # Check that an empty dict is returned
    load = resp.json()
    assert load == {}


def test_channel_join(clear_data, channel_set_up):
    '''
    Test that an join is successful

    Parameters:
        None

    Returns:
        Empty dictionary
    '''
    # Invite the user to the channel
    user = register_user(config.url + 'auth/register/v2', 'shelbygoodkind@testemail.com', 'testpassworkdas14', 'shelby', 'goodkind')
    data = {'token' : channel_set_up[0].get('token'), 'channel_id' : channel_set_up[3].get('channel_id'), 'u_id': user.get('u_id')}
    requests.post(config.url + 'channel/invite/v2', json=data)

    user_join_info = {'token' : user.get('token'), 'channel_id' : channel_set_up[3].get('channel_id')}

    load = requests.post(config.url + 'channel/join/v2', json=user_join_info)
    assert load.status_code == 200

def test_channel_details(clear_data, channel_set_up):
    '''
    Test that an retreival of channel details is successful

    Parameters:
        None

    Returns:
        Dictionary of channel information
    '''
    data = data = {'token' : channel_set_up[0].get('token'), 'channel_id' : channel_set_up[3].get('channel_id')}
    resp = requests.get(config.url + 'channel/details/v2', params=data)
    assert resp.status_code == 200

    load = resp.json()
    assert len(load['owner_members']) == 2
    assert load['name'] == 'motherland'
    assert len(load['all_members']) == 2

def test_channel_messages(clear_data, message_chan_setup):
    '''
    Test that an invite is successful

    Parameters:
        None

    Returns:
        Dictionary with a list of messages, start and end where start and end is the interval of the message index
        that the messages correspond to
    '''
    
    data = {'token' : message_chan_setup[0].get('token'), 'channel_id' : message_chan_setup[3].get('channel_id'), 'start' : 0}
    resp = requests.get(config.url + 'channel/messages/v2', params=data)

    assert resp.status_code == 200

    load = resp.json()

    assert len(load['messages']) == 12
    assert load['start'] == 0
    assert load['end'] == -1
    assert load['messages'][0]['message'] == 'works'
    assert load['messages'][11]['message'] == 'hello'

def test_channel_addowner(clear_data, channel_set_up):
    '''
    Test user is added as an owner successfully

    Parameters:
        None

    Returns:
        Empty dictionary
    '''
    user = register_user(config.url + 'auth/register/v2', 'shelbygoodkind@testemail.com', 'testpassworkdas14', 'shelby', 'goodkind')
    
    addowner_info = {'token' : channel_set_up[0].get('token'), 'channel_id' : channel_set_up[3].get('channel_id'), 'u_id' : user.get('auth_user_id')}

    resp = requests.post(config.url + 'channel/addowner/v1', json=addowner_info)
    
    assert resp.status_code == 200

def test_dreams_addowner(clear_data, channel_set_up):
    '''
    Test that user is added as an owner successfully if a dreams member who is not a member of the channel

    Parameters:
        None

    Returns:
        Empty dictionary
    '''
    # Change user's permission to global permission 1
    user = register_user(config.url + 'auth/register/v2', 'shelbygoodkind@testemail.com', 'testpassworkdas14', 'shelby', 'goodkind')

    permission_data = {
        'token': channel_set_up[0].get('token'), 
        'u_id' : user.get('auth_user_id'), 
        'permission_id': 1
    }
    requests.post(config.url + 'admin/userpermission/change/v1', json=permission_data)
    
    addowner_info = {'token' : channel_set_up[0].get('token'), 'channel_id' : channel_set_up[3].get('channel_id'), 'u_id' : user.get('auth_user_id')}

    resp = requests.post(config.url + 'channel/addowner/v1', json=addowner_info)
    assert resp.status_code == 200

def test_channel_removeowner(clear_data, channel_set_up):
    '''
    Test that user is removed as an owner successfully

    Parameters:
        None

    Returns:
        Empty dictionary
    '''
    removeowner_info = {'token' : channel_set_up[0].get('token'), 'channel_id' : channel_set_up[3].get('channel_id'), 'u_id' : channel_set_up[1].get('auth_user_id')}

    resp = requests.post(config.url + 'channel/removeowner/v1', json=removeowner_info)

    assert resp.status_code == 200

def test_channel_leave(clear_data, channel_set_up):
    '''
    Test that user leaves channel successfully

    Parameters:
        None

    Returns:
        Empty dictionary
    '''
    user_leave = {'token' : channel_set_up[2].get('token'), 'channel_id' : channel_set_up[3].get('channel_id')}

    resp = requests.post(config.url + 'channel/leave/v1', json=user_leave)

    assert resp.status_code == 200
    
