from src.other import clear_v1
from src.channel import channel_join_v2, channel_invite_v2
from src.channels import channels_create_v2
from src.auth import auth_register_v2
from src.message import message_send_v2
from src.error import AccessError, InputError
from src.data import data
from src.dm import dm_invite_v1, dm_create_v1
import pytest
from tests.fixture import dm_set_up, auth_set_up, channel_set_up

"""
Inviting a user to an existing dm

Arguments: 
    token (str) - the user's token that is requesting
    dm_id (int) - the dm's id
    u_id (int) - the user's u_id that is being changed

Exceptions:
    InputError - dm_id does not refer to an existing dm.
    InputError - u_id does not refer to a valid user.
    AccessError - the authorised user is not already a member of the DM

Returns:
    None
"""

def test_functionality(auth_set_up):
    #Test that dm invite successfully adds user to dm

    #register a third user
    auth_user_id3 = auth_register_v2('spencerreid@testemail.com', 'testpassworhj1245', 'spencer', 'reid')
    
    # dm_create(token, [u_id])
    dm_id = dm_create_v1(auth_set_up[0]['token'], [auth_set_up[1]['auth_user_id']])
    # dm_invite(token, dm_id, u_id)
    dm_invite_v1(auth_set_up[0]['token'], dm_id['dm_id'], auth_user_id3['auth_user_id'])

    # need to ask why u_id's length is the iterator in dm_create
    assert data['dm'][0]['all_members'] == [
        {'u_id' : 1, 'email' : 'validemail@gmail.com', 'name_first' : 'Hayden', 'name_last' : 'Everesty', 'handle_str' : 'haydeneveresty', 'profile_img_url' : ''},
        {'u_id' : 2, 'email' : 'validemail01@gmail.com', 'name_first' : 'Kim', 'name_last' : 'Nguyen', 'handle_str' : 'kimnguyen', 'profile_img_url' : ''},
        {'u_id' : 3, 'email' : 'spencerreid@testemail.com', 'name_first' : 'spencer', 'name_last' : 'reid', 'handle_str' : 'spencerreid', 'profile_img_url' : ''}
        
    ]
    assert data['dm'][0]['dm_name'] == 'haydeneveresty, kimnguyen, spencerreid'

def test_invite_many():
    #Test that dm invite is able to invite the same user to multiple dms

    clear_v1()

    auth_user_id1 = auth_register_v2('jenniferjj@testemail.com', 'testpassword12', 'jennifer', 'jareau')
    auth_user_id2 = auth_register_v2('emilyprentiss@testemail.com', 'testpassword13', 'emily', 'prentiss')
    auth_user_id3 = auth_register_v2('penelopegarcia@testemail.com', 'testpassword14','penelope', 'garcia')
    
    user_list = [auth_user_id2['auth_user_id']]
    # dm_create(token, [u_id])
    dm_id1 = dm_create_v1(auth_user_id1['token'], user_list)
    dm_id2 = dm_create_v1(auth_user_id1['token'], user_list)
    dm_id3 = dm_create_v1(auth_user_id1['token'], user_list)
    # dm_invite(token, dm_id, u_id)
    dm_invite_v1(auth_user_id1['token'], dm_id1['dm_id'], auth_user_id3['auth_user_id'])
    dm_invite_v1(auth_user_id1['token'], dm_id2['dm_id'], auth_user_id3['auth_user_id'])
    dm_invite_v1(auth_user_id2['token'], dm_id3['dm_id'], auth_user_id3['auth_user_id'])

    assert data['dm'][0]['all_members'] == [
        {'u_id' : 1, 'email' : 'jenniferjj@testemail.com', 'name_first' : 'jennifer', 'name_last' : 'jareau', 'handle_str' : 'jenniferjareau', 'profile_img_url' : ''},
        {'u_id' : 2, 'email' : 'emilyprentiss@testemail.com', 'name_first' : 'emily', 'name_last' : 'prentiss', 'handle_str' : 'emilyprentiss', 'profile_img_url' : ''},
        {'u_id' : 3, 'email' : 'penelopegarcia@testemail.com', 'name_first' : 'penelope', 'name_last' : 'garcia', 'handle_str' : 'penelopegarcia', 'profile_img_url' : ''}
    ]

    assert data['dm'][1]['all_members'] == [
        {'u_id' : 1, 'email' : 'jenniferjj@testemail.com', 'name_first' : 'jennifer', 'name_last' : 'jareau', 'handle_str' : 'jenniferjareau', 'profile_img_url' : ''},
        {'u_id' : 2, 'email' : 'emilyprentiss@testemail.com', 'name_first' : 'emily', 'name_last' : 'prentiss', 'handle_str' : 'emilyprentiss', 'profile_img_url' : ''},
        {'u_id' : 3, 'email' : 'penelopegarcia@testemail.com', 'name_first' : 'penelope', 'name_last' : 'garcia', 'handle_str' : 'penelopegarcia', 'profile_img_url' : ''}
    ]

    assert data['dm'][2]['all_members'] == [
        {'u_id' : 1, 'email' : 'jenniferjj@testemail.com', 'name_first' : 'jennifer', 'name_last' : 'jareau', 'handle_str' : 'jenniferjareau', 'profile_img_url' : ''},
        {'u_id' : 2, 'email' : 'emilyprentiss@testemail.com', 'name_first' : 'emily', 'name_last' : 'prentiss', 'handle_str' : 'emilyprentiss', 'profile_img_url' : ''},
        {'u_id' : 3, 'email' : 'penelopegarcia@testemail.com', 'name_first' : 'penelope', 'name_last' : 'garcia', 'handle_str' : 'penelopegarcia', 'profile_img_url' : ''}
    ]

    assert data['dm'][0]['dm_name'] == 'emilyprentiss, jenniferjareau, penelopegarcia'
    assert data['dm'][1]['dm_name'] == 'emilyprentiss, jenniferjareau, penelopegarcia'
    assert data['dm'][2]['dm_name'] == 'emilyprentiss, jenniferjareau, penelopegarcia'
    
def test_inviter_not_mem(dm_set_up):
    #Test inputerror is raised when the inviting user is not a member of the dm

    auth_user_id3 = auth_register_v2('spencerreid@testemail.com', 'testpassworhj1245', 'spencer', 'reid')
    with pytest.raises(InputError):
        dm_invite_v1(auth_user_id3['token'], dm_set_up[2].get('dm_id'), auth_user_id3['auth_user_id'])

def test_dm_invalid(dm_set_up):
    #Test that dm invite raises InputError when dm does not exist

    bad_dm_id = {'dm_id' : 156312}  
    with pytest.raises(InputError):
        dm_invite_v1(dm_set_up[0].get('token'), bad_dm_id['dm_id'], dm_set_up[1].get('auth_user_id'))

def test_not_valid_user(dm_set_up):
    #Test that dm invite raises InputError when invalid user

    bad_user = {'auth_user_id' : 156132321}
    with pytest.raises(InputError):
        dm_invite_v1(dm_set_up[0].get('token'), dm_set_up[2].get('dm_id'), bad_user['auth_user_id'])

def test_user_already_mem(dm_set_up):
    #Test that dm invite raises AccessError when user is already member of dm

    with pytest.raises(AccessError):
        dm_invite_v1(dm_set_up[0].get('token'), dm_set_up[2].get('dm_id'), dm_set_up[1].get('auth_user_id'))
