import pytest
import requests
import json
from src import config
from http_tests.fixtures import clear_data, user_reg
from json import dump, loads


def test_register(clear_data):
    '''
    Test that user is successfully registered

    Parameters:
        email (str) : the user calling the function
        password (str): name of the channel
        name_first (str) : first name of user
        name_last (str) : last name of user

    Returns:
        Dictionary with auth_user_id and token
    '''
    # Sanity check to ensure data is clear
    assert clear_data == {}
    
    data = {
        'email' : 'jenniferjareau@testemail.com',
        'password' : 'testpassword1253',
        'name_first' : 'jennifer', 
        'name_last' : 'jareau',
    }
    # Send the user info to be registered into the system
    resp = requests.post(config.url + 'auth/register/v2', json=data)
    user1 = resp.json()
    assert user1['auth_user_id'] == 1

def test_already_reg(clear_data, user_reg):
    '''
    Test that input error is raised when user/email has already been used to register user

    Parameters:
        email (str) : the user calling the function
        password (str): name of the channel
        name_first (str) : first name of user
        name_last (str) : last name of user

    Returns:
        Dictionary with auth_user_id and token
    '''

    data = {
        'email' : 'jenniferjareau@testemail.com',
        'password' : 'testpassword1253',
        'name_first' : 'jennifer', 
        'name_last' : 'jareau',
    }
    user_reg = requests.post(config.url + 'auth/register/v2', json=data)
    # Test that an input error is raised
    assert user_reg.status_code == 400

def test_bad_email(clear_data):
    '''
    Test an input error is raised when an email is invalid format

    Parameters:
        None
    
    Returns:
        Inputerror status code 400
    '''

    data = {
        'email' : 'jenniferjarea',
        'password' : 'testpassword1253',
        'name_first' : 'jennifer', 
        'name_last' : 'jareau',
    }
    resp = requests.post(config.url + 'auth/register/v2', json=data)
    assert resp.status_code == 400

def test_bad_password(clear_data):
    '''
    Test an input error is raised when a passowrd is invalid

    Parameters:
        None
    
    Returns:
        Inputerror status code 400
    '''
    data = {
        'email' : 'jenniferjarea',
        'password' : 'hi',
        'name_first' : 'jennifer', 
        'name_last' : 'jareau',
    }
    resp = requests.post(config.url + 'auth/register/v2', json=data)
    assert resp.status_code == 400

def test_long_name_first(clear_data):
    '''
    Test an input error is raised when first name exceeds 1-50 characters

    Parameters:
        None
    
    Returns:
        Inputerror status code 400
    '''

    data = {
        'email' : 'jenniferjareau@testemail.com',
        'password' : 'testpassword1253',
        'name_first' : 'jenniferspenceremilyaaronpenelopederektaralukemattdave', 
        'name_last' : 'jareau',
    }
    resp = requests.post(config.url + 'auth/register/v2', json=data)
    assert resp.status_code == 400

def test_long_name_last(clear_data):
    '''
    Test an input error is raised when last name exceeds 1-50 characters

    Parameters:
        None
    
    Returns:
        Inputerror status code 400
    '''

    data = {
        'email' : 'jenniferjareau@testemail.com',
        'password' : 'testpassword1253',
        'name_first' : 'jennifer', 
        'name_last' : 'jareauprentisshotchnermorganreidrossialvezgarciasimmons',
    }
    resp = requests.post(config.url + 'auth/register/v2', json=data)
    assert resp.status_code == 400

def test_login(clear_data, user_reg):
    '''
    Test that user is successfully logged in

    Parameters:
        email (str) : the user calling the function
        password (str): name of the channel

    Returns:
        Dictionary with auth_user_id and token
    '''
 
    data = {
        'email' : 'jenniferjareau@testemail.com',
        'password' : 'testpassword1253',
    }
    # Send the user info to be registered into the system
    requests.post(config.url + 'auth/register/v2', json=data)

    resp = requests.post(config.url + 'auth/login/v2', json=data)
    logged_user1 = resp.json()

    assert logged_user1['auth_user_id'] == 1


def test_bad_login(clear_data, user_reg):
    '''
    Test that user is successfully logged in

    Parameters:
        email (str) : the user calling the function
        password (str): name of the channel

    Returns:
        Dictionary with auth_user_id and token
    '''

    bad_login_data = {'email' : 'jenniferjareau@testemail.com', 'password' : 'notthepassword62'}
    resp = requests.post(config.url + 'auth/login/v2', json=bad_login_data)
    # Test that an input error is raised
    assert resp.status_code == 400

def test_logout(clear_data, user_reg):
    '''
    Test that user is successfully logged out

    Parameters:
        token (str) : the user logging out 

    Returns:
        is_success (bool) : whether the user has successfully logged out
    '''
    # Logout the user
    resp = requests.post(config.url + 'auth/logout/v1', json={'token' : user_reg.get('token')})
    logout_status = resp.json()
    assert logout_status['is_success']


def test_reset_code_invalid(clear_data, user_reg):
    '''
    Test that an input error is raised when the reset code is incorrect

    Parameters:
        None

    Returns:
        N/A
    '''
    email = 'jenniferjareau@testemail.com'
    request_data = {'email' : email}

    requests.post(config.url + 'auth/passwordreset/request/v1', json=request_data)

    reset_data = {
        'reset_code' : 'notthecode',
        'new_password' : 'bananasareyellow',
    }
    resp = requests.post(config.url + 'auth/passwordreset/reset/v1', json=reset_data)

    assert resp.status_code == 400


def test_reset_request(clear_data, user_reg):
    
    data = {'email': 'jenniferjareau@testemail.com'}
    resp = requests.post(config.url + 'auth/passwordreset/request/v1', json=data)

    assert resp.status_code == 200

def test_reset_request_bad_email(clear_data, user_reg):

    data = {'email': 'jemcarstairs@testemail.com'}

    resp = requests.post(config.url + 'auth/passwordreset/request/v1', json=data)

    assert resp.status_code == 400
