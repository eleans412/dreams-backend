from src.auth import auth_register_v2
from src.channels import channels_create_v2
from src.data import getData
from src.users import users_all_v1
import pytest
from src.other import clear_v1
from src.error import InputError, AccessError
from tests.fixture import auth_set_up
import jwt

"""
Returns a list of all users and their associated details

Arguments:
    token (str) - the user's token

Exceptions:
    N/A

Return Value:
    users (list of dict) - each dictionary contains types: user
"""

def test_single_user(auth_set_up):
    #test case for two registered users
    
    list_all = users_all_v1(auth_set_up[0].get('token'))
    assert len(list_all['users']) == 2

def test_multiple_users():
    #test for multiple users
    
    clear_v1()
    auth_user_id1 = auth_register_v2('validemail@gmail.com', '123abc!@#', 'Hayden', 'Everest')

    list_all = users_all_v1(auth_user_id1['token'])
    assert len(list_all['users']) == 1
    assert list_all['users'][0].get('name_first') == 'Hayden'

def test_no_token():
    with pytest.raises(AccessError):
        users_all_v1(None)