import pytest
import requests
import json
from http_tests.fixtures import clear_data, message_chan_setup, channel_set_up
from src import config

 
def test_user_remove(clear_data, message_chan_setup):
    '''
    Test that user is successfully removed from the dreams server

    Parameters:
        token(str): the calling to remove from Dreams
        u_id (int): the user being removed from Dreams
    
    Returns:
        Empty Dictionary
    '''
    data = {
        'token' : message_chan_setup[0].get('token'),
        'u_id': message_chan_setup[2].get('auth_user_id')
    }
    resp = requests.delete(config.url + 'admin/user/remove/v1', json=data)
    assert resp.status_code == 200


def test_change_permission(clear_data, channel_set_up):
    '''
    Test that the permissions of users are successfully changed

    Parameters:
        token (str): the user calling for the change in permissions
        u_id (int): the user who's permissions are to be changed

    Returns:
        Empty Dictionary
    '''
    assert clear_data == {}

    data = {'token': channel_set_up[0].get('token'), 'u_id' : channel_set_up[1].get('auth_user_id'), 'permission_id': 1}
    resp = requests.post(config.url + 'admin/userpermission/change/v1', json=data)
    assert resp.status_code == 200
