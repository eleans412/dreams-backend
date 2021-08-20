from src.auth import auth_register_v2, auth_login_v2, auth_logout_v1
from src.data import getData
from src.users import users_stats_v1
from src.channels import channels_create_v2, channels_listall_v2
from src.message import message_send_v2, message_senddm_v1
from src.dm import dm_create_v1
from src.error import AccessError
import pytest
from src.other import clear_v1
from src.error import InputError 
from tests.fixture import auth_set_up, channel_set_up, dm_set_up
import jwt

"""
Fetches the required statistics about this user's use of UNSW Dreams
    
Arguments:
    token (str) - the user's token

Exceptions:
    N/A

Return Value:
    dreams_stats (dict) - Dictionary of shape: 
        - channels_exist (int)
        - dms_exist (int)
        - messages_exist (int)
        - utilization_rate (float)
"""

def test_zero_users():
    #test users stats for zero existing users
        
    clear_v1()
    with pytest.raises(AccessError):
        users_stats_v1('badtoken')

def test_zero_utilization():
    #two users exist, but have not used any dreams functionality

    auth_user_id1 = auth_register_v2('validemail@gmail.com', '123abc!@#', 'Karena', 'Nguyen')
    auth_register_v2('validemail01@gmail.com', '123abc#5000', 'Eleanor', 'Au' )

    stats = users_stats_v1(auth_user_id1['token'])

    channels_exist = stats['dreams_stats'].get('channels_exist')[0].get('num_channels_exist')
    dms_exist = stats['dreams_stats'].get('dms_exist')[0].get('num_dms_exist')
    messages_exist = stats['dreams_stats'].get('messages_exist')[0].get('num_messages_exist')
    assert channels_exist == 0
    assert dms_exist == 0
    assert messages_exist == 0
    assert stats['dreams_stats'].get('utilization_rate') == 0


def test_involved_user(auth_set_up):
    #check functionality for a more involved users

    #create two channels, one public one private
    channel_id1 = channels_create_v2(auth_set_up[0]["token"], 'Room 1', True)
    channel_id2 = channels_create_v2(auth_set_up[0]["token"], 'Room 2', False)

    #send a message to both channels
    message_send_v2(auth_set_up[0]['token'], channel_id1['channel_id'], 'hello')
    message_send_v2(auth_set_up[0]['token'], channel_id2['channel_id'], 'Hello Again')


    #check DREAMS stats
    stats1 = users_stats_v1(auth_set_up[0]['token'])
    
    # Get specific keys for num of channels, dms and messages activity
    channels_exist = stats1['dreams_stats'].get('channels_exist')[-1].get('num_channels_exist')
    dms_exist = stats1['dreams_stats'].get('dms_exist')[-1].get('num_dms_exist')
    messages_exist = stats1['dreams_stats'].get('messages_exist')[-1].get('num_messages_exist')
    assert channels_exist == 2
    assert dms_exist == 0
    assert messages_exist == 2
    assert stats1['dreams_stats'].get('utilization_rate') == 0.5

    # Add another channel, dm and message then call dreams stats
    channels_create_v2(auth_set_up[0]["token"], 'Room 2', True)
    dm1 = dm_create_v1(auth_set_up[0]['token'], [auth_set_up[1]['auth_user_id']])
    message_senddm_v1(auth_set_up[0]['token'], dm1['dm_id'], "yo whats up")

    updated_stats = users_stats_v1(auth_set_up[0]['token'])

    channels_exist = updated_stats['dreams_stats'].get('channels_exist')[-1].get('num_channels_exist')
    dms_exist = updated_stats['dreams_stats'].get('dms_exist')[-1].get('num_dms_exist')
    messages_exist = updated_stats['dreams_stats'].get('messages_exist')[-1].get('num_messages_exist')
    assert channels_exist == 3
    assert dms_exist == 1
    assert messages_exist == 3 
    assert updated_stats['dreams_stats'].get('utilization_rate') == 1.0