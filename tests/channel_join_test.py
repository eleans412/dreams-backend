from src.other import clear_v1
from src.channel import channel_join_v2, channel_invite_v2
from src.channels import channels_create_v2
from src.auth import auth_login_v2, auth_register_v2
from src.admin import admin_userpermissions_change_v1
from src.error import AccessError, InputError
from src.data import data
import pytest
from tests.fixture import channel_set_up, auth_set_up

"""
Given a channel_id of a channel that the authorised user can join, adds them to that channel

Arguments:
    token (str) - the user's token
    channel_id (int) - the channel's id

Exceptions:
    InputError - Channel ID is not a valid channel
    AccessError - channel_id refers to a channel that is private

Return Value:
    None
"""

# Channel_join_v2 tests
# ================================================

def test_channel_join(channel_set_up):
    #Test functionality of channel_join_v2. Returning an altered user dictionary with 
    #channel now in the list of channels they are part of 
    
    # Loop to find the location of the user that joined the channel
    # Iterate through list of users
    count = 0
    location = 0
    for person in data['users']:
        if person.get('auth_user_id') == channel_set_up[1].get('auth_user_id'):
            # Mark location of the user in dictionary
            location = count
            # Break from loop once user is found
            break
        else:
            count += 1

    # Loop through the list of channels the user is in to see if channel
    # successfully added 
    assert len(data['users'][location]['channels_in']) == 1

def test_if_multiple_channels(channel_set_up):
    #Test if able to loop through data['channels'] if there is more than one channel, 
    #returning an altered users dictionary

    # set up some additional channels extra to those from channel set up
    channel_id2 = channels_create_v2(channel_set_up[0]['token'], 'campjupiter', True)
    
    #2nd user then joins one more channel out of the two created above
    channel_join_v2(channel_set_up[1]['token'], channel_id2['channel_id'])


    # Loop to find the location of the user that joined the channel
    # Iterate through list of users
    count = 0
    location = 0
    for person in data['users']:
        if person.get('auth_user_id') == channel_set_up[1]['auth_user_id']:
            # Mark location of the user in dictionary
            location = count
            # Break from loop once user is found
            break
        else:
            count += 1

    # Check the user is successfully added to the channel 
    assert len(data['users'][location]['channels_in']) == 2

    # Loop through the list of channels the user is in to see if channel
    # successfully added 
    channel_list = []
    for user in data['users']:
        if user.get('auth_user_id') is channel_set_up[1]['auth_user_id']:
            for channel in user.get('channels_in'):
                channel_list.append(channel['channel_id'])
    assert channel_list == [1, 2]

def test_auth_user_id_bad():
    #Tests that InputError is raised if auth_user_id does not exist

    # Clear any preset info in data
    clear_v1()
    # Register and login 2 users
    auth_user_id1 = auth_register_v2('jenniferjj@testemail.com', 'testpassword12', 'jennifer', 'jareau')
    
    # Generate auth_id info for users that have not been registered
    bad_user_id = {'token' : [1030]}
   
    # Generate channel to be added to
    channel_id = channels_create_v2(auth_user_id1['token'], 'testchannel1', True)

    # Raise InputError if the auth_user_id does not exist
    with pytest.raises(InputError):
        channel_join_v2(bad_user_id['token'], channel_id['channel_id'])

def test_channel_id_not_exist(auth_set_up):
    #Test that InputError is raised if the channel_id does not exist

    # Generate bad channel that has not been created
    bad_channel = {'channel_id' : 24601}
    
    # Create channel so that data['channels'] is generated to loop through
    channel_id = channels_create_v2(auth_set_up[1].get('token'), 'criminalminds', True)
    channel_invite_v2(auth_set_up[1].get('token'), channel_id['channel_id'], auth_set_up[0].get('auth_user_id'))

    with pytest.raises(InputError):
        channel_join_v2(auth_set_up[0].get('token'), bad_channel['channel_id'])


def test_private_channel(auth_set_up):
    #Test that AccessError is raised when channel is private and user is not global owner

    # Set up necessary inputs for channel_join
    auth_user_id3 = auth_register_v2('groverunder@testemail.com', 'passoRdW3', 'grover', 'underwood')

    channel_id = channels_create_v2(auth_set_up[0].get('token'), 'camphalfblood', False)

    channel_invite_v2(auth_set_up[0].get('token'), channel_id['channel_id'], auth_set_up[1].get('auth_user_id'))
    channel_invite_v2(auth_set_up[0].get('token'), channel_id['channel_id'], auth_user_id3['auth_user_id'])

    with pytest.raises(AccessError):
        channel_join_v2(auth_user_id3['token'], channel_id['channel_id'])


def test_joined_multiple_channels(channel_set_up):
    #Test to join mulitple channels

    #generate an additional user, and 2 more channels to join
    auth_user_id3 = auth_register_v2('validemail3@gmail.com', '123abc!@#', 'Bennett', 'Frerck')
    channel_id2 = channels_create_v2(channel_set_up[0]['token'], 'theclave', True)
    channel_id3 = channels_create_v2(channel_set_up[0]['token'], 'hogwarts', True)
    
    
    #join channels 2 and 3
    channel_join_v2(channel_set_up[1]['token'], channel_id2['channel_id'])
    channel_join_v2(channel_set_up[1]['token'], channel_id3['channel_id'])

    
    # Join all 3 channels
    channel_join_v2(auth_user_id3['token'], channel_set_up[2]['channel_id'])
    channel_join_v2(auth_user_id3['token'], channel_id2['channel_id'])
    channel_join_v2(auth_user_id3['token'], channel_id3['channel_id'])
    
    # Loop through the list of channels the user is in to see if channel
    # successfully added 
    channel_list = []
    for user in data['users']:
        if user.get('auth_user_id') is auth_user_id3['auth_user_id']:
            for channel in user.get('channels_in'):
                channel_list.append(channel['channel_id'])
    assert channel_list == [1, 2, 3]

def test_global_owner_join_private(auth_set_up):

    # Set user 2 to be a global owner
    admin_userpermissions_change_v1(auth_set_up[0].get('token'), auth_set_up[1].get('auth_user_id'), 1)

    # Create a private channel
    channel_id = channels_create_v2(auth_set_up[0].get('token'), 'camphalfblood', False)
    
    channel_join_v2(auth_set_up[1].get('token'), channel_id.get('channel_id'))

    # Check that the user has been successfully added to the channel and the channel id is added to their
    # Channels in key
    assert data['users'][auth_set_up[1].get('auth_user_id') - 1].get('channels_in')[0]['channel_id'] == 1
    assert len(data['channels'][channel_id.get('channel_id') - 1]['all_members']) == 2
    assert len(data['channels'][channel_id.get('channel_id') - 1]['owner_members']) == 2

def test_invalid_channel_id(auth_set_up):
    #Test that the wrong input raises an inputerror

    with pytest.raises(InputError): 
        channel_join_v2(auth_set_up[1].get('token'), 'hey')