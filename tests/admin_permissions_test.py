from src.other import clear_v1
from src.auth import auth_register_v2, auth_login_v2
from src.admin import admin_userpermissions_change_v1
from src.channels import channels_create_v2
from src.channel import channel_invite_v2, channel_join_v2, channel_addowner_v1
from src.error import AccessError, InputError
from src.data import data
import pytest
from tests.fixture import channel_set_up, auth_set_up

"""
Given a user by their u_id, change their permissions to the one input by permission_id

Arguments:
    token (str) - the user's token that is requesting permission change
    u_id (int) - the user's u_id that is having their permission changed
    permission_id (int) - the user's permission as a member or owner

Exceptions:
    InputError - u_id does not refer to a valid user
    InputError - permission_id does not refer to a value permission
    AccessError - The authorised user is not an owner

Return Value:
    None
"""

def test_change_global(channel_set_up):
    #Test that the user's permissions have been successfully changed in the global scope

    admin_userpermissions_change_v1(channel_set_up[0].get('token'), channel_set_up[1].get('auth_user_id'), 1)

    for user in data['users']:
        if user.get('auth_user_id') is channel_set_up[1].get('auth_user_id'):
            check_permission = user.get('global_permissions')
    
    assert check_permission == 1

def test_invalid_user(channel_set_up):
    #Test that InputError is raised when u_id is not valid

    bad_user = {'auth_user_id' : 16532}

    with pytest.raises(InputError):
        admin_userpermissions_change_v1(channel_set_up[0].get('token'), bad_user['auth_user_id'], 3)

def test_not_permission_val(channel_set_up):
    #Test that InputError is raised when user's permissions value is invalid

    with pytest.raises(InputError):
        admin_userpermissions_change_v1(channel_set_up[0].get('token'), channel_set_up[1].get('auth_user_id'), 8)

def test_not_owner():
    # Check that permission id is already set for global and channel 
    # Raise Input Error if so
    
    clear_v1()
    user1 = auth_register_v2('taylorhickson@testemail.com','password11', 'taylor', 'hickson')
    user2 = auth_register_v2('amaliaholm@testemail.com', 'password12', 'amalia', 'holm')

    with pytest.raises(AccessError):
        admin_userpermissions_change_v1(user2['token'], user1['auth_user_id'], 1)

def test_invalid_token(channel_set_up):
    #Test that InputError is raised when token belongs to an invalid user

    bad_user = {
        'auth_user_id' : 561321,
        'token' : 'asiofjvlknvsdkjnvsoikmnjpivsd',
    }

    with pytest.raises(InputError):
        admin_userpermissions_change_v1(bad_user['token'], channel_set_up[0].get('auth_user_id'), 1)

def test_one_global_owner():
    #Test that InputError is raised when there is only one global owner

    clear_v1()
    user1 = auth_register_v2('taylorhickson@testemail.com','password11', 'taylor', 'hickson')

    with pytest.raises(InputError):
        admin_userpermissions_change_v1(user1['token'], user1['auth_user_id'], 2)

def test_change_existing_permission(auth_set_up):
    #Test that InputError is raised when the user already has the permission value inputted

    with pytest.raises(InputError):
        # Check that permission id is already set for global and channel 
        # Raise Input Error if so
        admin_userpermissions_change_v1(auth_set_up[0].get('token'), auth_set_up[1].get('auth_user_id'), 2)