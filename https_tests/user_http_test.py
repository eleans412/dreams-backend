import pytest
import requests
import json
from http_tests.http_helpers import register_user
from http_tests.fixtures import clear_data, user_reg, channel_set_up
from src import config

def test_user_profile(clear_data, user_reg): 
    '''
    Test that the user profile is successfully returned

    Parameters:
        token (str): the token authenticating the user calling this function
        u_id (int): the user that the profile belongs to

    Returns:
        Dictionary with the user info
    '''
    data = {
        'token' : user_reg.get('token'),
        'u_id' : user_reg.get('auth_user_id'),
    }

    resp = requests.get(config.url + 'user/profile/v2', params=data)
    
    load = resp.json()
    assert load.get('user')['name_first'] == 'jennifer'

def test_invalid_user(clear_data, user_reg):
    '''
    Test that the user profile raises input error when u_id is not valid

    Parameters:
        token (str): the token authenticating the user calling this function
        u_id (int): the user that the profile belongs to

    Returns:
        Dictionary with the user info
    '''
    
    data = {
        'token' : user_reg.get('token'),
        'u_id' : 61532,
    }
    resp = requests.get(config.url + 'user/profile/v2', params=data)

    assert resp.status_code == 400

def test_setname(clear_data, user_reg): 
    '''
    Test that the user name is changed

    Parameters:
        token (str): the token authenticating the user calling this function
        name_first (str) : first name to be set
        name_last (str) : last name to be set

    Returns:
        Empty Dictionary 
    '''
    data = {
        'token' : user_reg.get('token'),
        'name_first' : 'andrea',
        'name_last' : 'cook'
    }
    resp = requests.put(config.url + 'user/profile/setname/v2', json=data)

    assert resp.status_code == 200

def test_name_first_long(clear_data, user_reg):
    '''
    Test that the input error is raised when name_first is longer than 50 characters

    Parameters:
        token (str): the token authenticating the user calling this function
        name_first (str) : first name to be set
        name_last (str) : last name to be set
        
    Returns:
        Empty Dictionary 
    '''
    data = {
        'token' : user_reg.get('token'),
        'name_first' : 'jenniferemilydavemattlukepenelopespenceraarontaraderek',
        'name_last' : 'cook'
    }
    resp = requests.put(config.url + 'user/profile/setname/v2', json=data)

    assert resp.status_code == 400

def test_name_last_long(clear_data, user_reg):
    '''
    Test that the input error is raised when name_last is longer than 50 characters

    Parameters:
        token (str): the token authenticating the user calling this function
        name_first (str) : first name to be set
        name_last (str) : last name to be set
        
    Returns:
        Empty Dictionary 
    '''
    data = {
        'token' : user_reg.get('token'),
        'name_first' : 'andrea',
        'name_last' : 'jareauprentisshotchnermorganreidrossialvezgarciasimmons'
    }
    resp = requests.put(config.url + 'user/profile/setname/v2', json=data)

    assert resp.status_code == 400


def test_setemail(clear_data, user_reg): 
    '''
    Test that the user email is successfully changed

    Parameters:
        token (str): the token authenticating the user calling this function
        email (str): the email to be set

    Returns:
        Empty Dictionary
    '''

    data = {
        'token' : user_reg.get('token'),
        'email' : 'tonishalifoe@testemail.com',
    }
    resp = requests.put(config.url + 'user/profile/setemail/v2', json=data)

    assert resp.status_code == 200

def test_email_invalid(clear_data, user_reg):
    '''
    Test that the user email is successfully changed

    Parameters:
        token (str): the token authenticating the user calling this function
        email (str): the email to be set

    Returns:
        Empty Dictionary
    '''
    data = {
        'token' : user_reg.get('token'),
        'email' : 'tonishalifoe',
    }
    resp = requests.put(config.url + 'user/profile/setemail/v2', json=data)

    assert resp.status_code == 400

def test_email_already_used(clear_data, user_reg):
    '''
    Test that the user email is successfully changed

    Parameters:
        token (str): the token authenticating the user calling this function
        email (str): the email to be set

    Returns:
        Empty Dictionary
    '''
    data = {
        'token' : user_reg.get('token'),
        'email' : 'jenniferjareau@testemail.com',
    }
    resp = requests.put(config.url + 'user/profile/setemail/v2', json=data)

    assert resp.status_code == 400

def test_sethandle(clear_data, user_reg):
    '''
    Test that the user profile is successfully returned

    Parameters:
        token (str): the token authenticating the user calling this function
        u_id (int): the user that the profile belongs to

    Returns:
        Dictionary with the user info
    '''

    data = {
        'token' : user_reg.get('token'),
        'handle_str' : 'jjfromthebau',
    }
    resp = requests.put(config.url + 'user/profile/sethandle/v1', json=data)

    assert resp.status_code == 200


def test_upload_photo_functionality(clear_data): 
    user = register_user(config.url + 'auth/register/v2', 'shelbygoodkind@testemail.com', 'testpassworkdas14', 'shelby', 'goodkind')
    data = {
        'token' : user.get('token'), 
        'img_url' : "https://pyxis.nymag.com/v1/imgs/4e7/109/9ca3a0b4352ca3ff74b89cb208ceda6ab5-kidney-bean.jpg" , 
        'x_start' : 0,
        'y_start' : 0, 
        'x_end' : 30, 
        'y_end': 30, 
        }
    
    resp = requests.post(config.url + 'user/profile/uploadphoto/v1', json=data)
    assert resp.status_code == 200

    # Check that an empty dict is returned
    load = resp.json()
    assert load == {}

def test_user_stats(clear_data, channel_set_up):
    '''
    Test that the user stats is successfully returned

    Parameters:
        channel_set_up(fixture)

    Returns:
        Dictionary with the user stats
    '''

    data = {'token' : channel_set_up[0].get('token')}

    resp = requests.get(config.url + 'user/stats/v1', params=data)

    load = resp.json()

    assert resp.status_code == 200
    assert load['user_stats'].get('channels_joined')[0].get('num_channels_joined') == 2
    assert load['user_stats'].get('dms_joined')[0].get('num_dms_joined') == 0
    assert load['user_stats'].get('messages_sent')[0].get('num_messages_sent') == 0
    
