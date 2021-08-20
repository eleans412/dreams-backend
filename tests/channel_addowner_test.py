from src.data import data
from src.channel import channel_addowner_v1, channel_invite_v2, channel_join_v2
from src.channels import channels_create_v2
from src.auth import auth_register_v2, auth_login_v2
from src.helper import generate_token, get_timestamp
from src.error import InputError, AccessError
from src.other import clear_v1
import pytest
from tests.fixture import channel_set_up

"""
Make user with user id u_id an owner of this channel

Arguments:
    token (str) - the user's token that is requesting
    channel_id (int) - the channel's id
    u_id (int) - the user's id that is being changed

Exceptions:
    InputError - Channel ID is not a valid channel
    InputError - When user with user id u_id is already an owner of the channel
    AccessError - when the authorised user is not an owner of the **Dreams**, or an owner of this channel

Return Value:
    None
"""

def test_functionality(channel_set_up):
    #Test channel is made an owner of the channel successfully

    channel_addowner_v1(channel_set_up[0].get('token'), 
    channel_set_up[2].get('channel_id'), 
    channel_set_up[1].get('auth_user_id'))

    # Check the owner has been successfully added to the owner's list
    owner_list = []
    for user in data['channels']:
        if user.get('channel_id') is channel_set_up[2].get('channel_id'):
            for owner in user.get('owner_members'):
                owner_list.append(owner.get('u_id'))
    assert owner_list == [1, 2]

def test_not_valid_channel(channel_set_up):
    #Test an Input Error is raised when channel_id is not valid

    bad_channel_id = {'channel_id' : 123545}
    with pytest.raises(InputError):
        channel_addowner_v1(channel_set_up[0].get('token'), 
        bad_channel_id['channel_id'], 
        channel_set_up[1].get('auth_user_id'))

def test_dreams_owner(channel_set_up):
    #Test channel is made an owner of the channel successfully if **Dreams** owner adds the user

    #Dreams owners adds second user as a channel owner
    channel_addowner_v1(channel_set_up[0]['token'], 
    channel_set_up[2]['channel_id'], 
    channel_set_up[1]['auth_user_id'])

    # Check that user has been added successfully
    owner_list = []
    for user in data['channels']:
        if user.get('channel_id') is channel_set_up[2]['channel_id']:
            for owner in user.get('owner_members'):
                owner_list.append(owner.get('u_id'))
    assert owner_list == [1, 2]

def test_user_already_owner(channel_set_up):
    #Test that Input Error is raised when the user is already an owner of the channel

    channel_addowner_v1(channel_set_up[0].get('token'), 
    channel_set_up[2].get('channel_id'), 
    channel_set_up[1].get('auth_user_id'))

    with pytest.raises(AccessError):
        channel_addowner_v1(channel_set_up[1].get('token'), 
        channel_set_up[2].get('channel_id'), 
        channel_set_up[0].get('auth_user_id'))

def test_user_not_exist(channel_set_up):
    #Test that an Input Error is raised when the user passed in is not a valid user

    bad_user_id = {'auth_user_id' : 5613543}
    with pytest.raises(InputError):
        channel_addowner_v1(channel_set_up[0].get('token'), 
        channel_set_up[2].get('channel_id'), 
        bad_user_id['auth_user_id'])

def test_user_not_owner(channel_set_up):
    #Test that an AccessError is raised when the user calling addowner is not an owner of the channel 
    #or an owner of **Dreams**

    user_id3 = auth_register_v2('celiciusgames@testemail.com', 'testpassword13', 'peter', 'allgrove')
    with pytest.raises(AccessError):
        channel_addowner_v1(channel_set_up[1].get('token'), channel_set_up[2].get('channel_id'), user_id3['auth_user_id'])

def test_wrong_input():
    '''
    Test that the wrong input raises an inputerror

    Parameters:
        None

    Returns:
        N/A
    '''
    clear_v1()
    auth_user_id_new = auth_register_v2('example_email23@gmail.com', '123abc!@#', 'Jacob', 'Smith') 
    
    with pytest.raises(InputError):
        channel_addowner_v1(auth_user_id_new["token"], auth_user_id_new['auth_user_id'], 123)
