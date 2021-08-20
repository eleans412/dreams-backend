from src.data import getData
from src.error import InputError, AccessError
from src.helper import get_end_nums, check_valid, find_user_id, get_timestamp, all_chan_count
from src.helper import all_dm_count, all_message_count, get_timestamp, get_utilization_rate
from src.channels import channels_listall_v2, channels_list_v2
from src.dm import dm_list_v1
import re

def users_all_v1(token):
    """
    Returns a list of all users and their associated details

    Arguments:
        token (str) - the user's token
    
    Exceptions:
        N/A
    
    Return Value:
        users (list of dict) - each dictionary contains types: user
    """
    data = getData()

    token_valid = find_user_id(token)
    if token_valid == False:
        raise AccessError(description = 'User not registered in Dreams')
   
    users_list = {'users' : []}
    for user in data['users']:
        user_dict = {
            "u_id": user.get('auth_user_id'),
            "email": user.get('email'),
            "name_first": user.get('f_name'),
            "name_last": user.get('l_name'),
            "handle_str": user.get('handle_str')
        }
        users_list['users'].append(user_dict)

    return users_list

def users_stats_v1(token):
    """
    Fetches the required statistics about this user's use of UNSW Dreams
        
    Arguments:
        token (str) - the user's token

    Exceptions:
        N/A

    Return Value:
        dream_stats (dict) - Dictionary of shape: 
            - channels_exist (int)
            - dms_exist (int)
            - message_exist (int)
            - utilization_rate (float)
    """
    data = getData()
    empty_stats = False


    # Get the current timestamp
    time_stamp = get_timestamp()

    auth_user_id = find_user_id(token)
    if auth_user_id == False:
        raise AccessError(description = 'User is not a registered user')


    #set desired stats to zero
    num_dreams_channels = 0
    num_dreams_dms = 0
    num_dreams_msgs = 0


    #find total number of dreams channels
    num_dreams_channels = all_chan_count()

    #find total number of dreams dms
    num_dreams_dms = all_dm_count()

    #find total number of dreams messages
    num_dreams_msgs = all_message_count()

    #find number of users who have joined at least one channel or dm
    active_users = 0
    for user in data['users']:
        if 'channels_in' in user:
            active_users += 1
        elif 'dms_in' in user:
            active_users += 1


    #find the total number of users
    total_users = len(data['users'])

    #calculate utilization rate
    utilization_rate = get_utilization_rate(active_users, total_users)

    # Add dreams_stats to the dream_stats key in the data structure
    # If there are no existing channels, dms and messages
    if data.get('dreams_stats') == None:
        data['dreams_stats'] = {
            'channels_exist' : [{'num_channels_exist' : num_dreams_channels, 'time_stamp': time_stamp}],
            'dms_exist' : [{'num_dms_exist' : num_dreams_dms, 'time_stamp' : time_stamp}], 
            'messages_exist' : [{'num_messages_exist' : num_dreams_msgs, 'time_stamp' : time_stamp}], 
            'utilization_rate' : round(utilization_rate, 1), 
        }
        empty_stats = True

    # If there is an existing dreams_stats data structure
    if not empty_stats:
        # Update the channels for all Dreams
        if num_dreams_channels > data['dreams_stats']['channels_exist'][-1]['num_channels_exist']:
            channel_dict = {'num_channels_exist' : num_dreams_channels, 'time_stamp': time_stamp}
            data['dreams_stats']['channels_exist'].append(channel_dict)

        # Update the dms for all Dreams
        if num_dreams_dms > data['dreams_stats']['dms_exist'][-1]['num_dms_exist']:
            dm_dict = {'num_dms_exist' : num_dreams_dms, 'time_stamp' : time_stamp}
            data['dreams_stats']['dms_exist'].append(dm_dict)
    
        # Update the messages for all Dreams
        if num_dreams_msgs > data['dreams_stats']['messages_exist'][-1]['num_messages_exist']:
            msg_dict = {'num_messages_exist' : num_dreams_msgs, 'time_stamp' : time_stamp}
            data['dreams_stats']['messages_exist'].append(msg_dict)

        #calculate involvment rate to update the rate for additional channels and dms
        utilization_rate = get_utilization_rate(active_users, total_users)
        data['dreams_stats']['utilization_rate'] = round(utilization_rate, 1)
    
    return {'dreams_stats' : data['dreams_stats']}
