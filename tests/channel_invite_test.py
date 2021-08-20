import pytest
from src.error import AccessError, InputError
from src.auth import auth_login_v2, auth_register_v2
from src.channels import channels_create_v2
from src.channel import channel_invite_v2
from src.admin import admin_userpermissions_change_v1
from src.other import clear_v1
from src.data import data
from tests.fixture import channel_set_up, auth_set_up

"""
Invites a user (with user id u_id) to join a channel with ID channel_id.
Once invited the user is added to the channel immediately

Arguments:
    token (str) - the user's token that is inviting the user to the channel
    channel_id (int) - the channel's id
    u_id (int) - the user's u_id that is being invited

Exceptions:
    InputError - channel_id does not refer to a valid channel.
    InputError - u_id does not refer to a valid user
    AccessError - the authorised user is not already a member of the channel

Return Value:
    None
"""

# Channel_invite_v2 tests
# ===========================================
def test_channel_invite_v2(auth_set_up):
    #Test channel_invite_v2 functionality and adds the second registered user to the channel

    # Create a new channel and invite
    channel_id = channels_create_v2(auth_set_up[0].get('token'), 'testchannel1', True)
    channel_invite_v2(auth_set_up[0].get('token'), channel_id['channel_id'], auth_set_up[1].get('auth_user_id'))

    # Check the user has been successfully added
    member_list = []
    for channel in data['channels']:
        if channel.get('channel_id') is channel_id['channel_id']:
            for member in channel.get('all_members'):
                member_list.append(member.get('u_id'))
    
    assert member_list == [1, 2]


def test_channel_id_bad(auth_set_up):
    #Test that InputError is raised when the channel_id does not exist

    # Generate channel to be added to, creating data['channels'] to iterate through
    channel_id = channels_create_v2(auth_set_up[0].get('token'), 'testchannel1', True)
    
    # Generate channel_id that does not exist in data
    bad_channel_id = {'channel_id' : 626}
    
    # Check that invite is successful for a registered test 
    channel_invite_v2(auth_set_up[0].get('token'), channel_id['channel_id'], auth_set_up[1].get('auth_user_id'))

    # Raise InputError if the channel does not exist
    with pytest.raises(InputError):
        channel_invite_v2(auth_set_up[0].get('token'), bad_channel_id['channel_id'], auth_set_up[1].get('auth_user_id'))

def test_channel_invalid(auth_set_up):
    #Test that the wrong input raises an inputerror

    # Raise InputError if the channel does not exist
    with pytest.raises(InputError):
        channel_invite_v2(auth_set_up[0].get('token'), 'hello', auth_set_up[1].get('auth_user_id'))


def test_user_bad(auth_set_up):
    #Tests that InputError is raised if u_id does not exist

    # Generate auth_id info for users that have not been registered
    bad_user_id = {'auth_user_id' : 1030}
    
    # Generate channel to be added to
    channel_id = channels_create_v2(auth_set_up[0].get('token'), 'testchannel1', True)

    # Raise Input Error if the user does not exist
    with pytest.raises(InputError):
        channel_invite_v2(auth_set_up[0].get('token'), channel_id['channel_id'], bad_user_id['auth_user_id'])
        

def test_auth_user_id_bad(auth_set_up):
    #Tests that InputError is raised if auth_user_id does not exist

    # Generate auth_id info for users that have not been registered
    bad_user_id = {'token' : [1030]}
   
    # Generate channel to be added to
    channel_id = channels_create_v2(auth_set_up[0].get('token'), 'testchannel1', True)

    # Raise InputError if the auth_user_id does not exist
    with pytest.raises(InputError):
        channel_invite_v2(bad_user_id['token'], channel_id['channel_id'], auth_set_up[1].get('auth_user_id'))
        

def test_user_not_member(auth_set_up):
    #Tests if AccessError is raised when the auth_user_id does exist
    #But the user does not belong to the channel

    # Create users that are not members of the channel
    auth_user_id3 = auth_register_v2('penelopegarcia@testemail.com', 'testpassword14','penelope', 'garcia')

    # Generate channel to be invited to
    channel_id = channels_create_v2(auth_set_up[0].get('token'), 'testchannel1', True)
    
    # Raise AccessError if the user is not in channel and attempting to invite
    with pytest.raises(AccessError):   
        channel_invite_v2(auth_user_id3['token'], channel_id['channel_id'], auth_set_up[1].get('auth_user_id'))
       
def test_global_owner(auth_set_up):
    # Create a new channel and invite
    channel_id = channels_create_v2(auth_set_up[0].get('token'), 'testchannel1', True)
    # Change user 2 to be a global owner
    admin_userpermissions_change_v1(auth_set_up[0].get('token'), auth_set_up[1].get('auth_user_id'), 1)

    channel_invite_v2(auth_set_up[0].get('token'), channel_id['channel_id'], auth_set_up[1].get('auth_user_id'))

    # Check the user has been successfully added
    member_list = []
    owner_list = []
    for channel in data['channels']:
        if channel.get('channel_id') is channel_id['channel_id']:
            for member in channel.get('all_members'):
                member_list.append(member.get('u_id'))
            for owner in channel.get('owner_members'):
                owner_list.append(owner.get('u_id'))

    assert member_list == [1, 2]
    assert owner_list == [1, 2]


def test_member_add(channel_set_up):
    #Test that a member can add users to the channel

    # Set up necessary inputs for channel_join
    auth_user_id3 = auth_register_v2('groverunder@testemail.com', 'passoRdW3', 'grover', 'underwood')

    # Have the new member invite another user
    channel_invite_v2(channel_set_up[1].get('token'), channel_set_up[2].get('channel_id'), auth_user_id3['auth_user_id'])
    
    # Loop through the list of channels the user is in to see if channel
    # successfully added 
    channel_list = []
    for user in data['users']:
        if user.get('auth_user_id') is auth_user_id3['auth_user_id']:
            for channel in user.get('channels_in'):
                channel_list.append(channel['channel_id'])
    
    assert channel_list == [1]

