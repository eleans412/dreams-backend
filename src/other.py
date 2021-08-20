from src.data import data
from src.helper import find_user_id, check_valid_info, check_search
from src.error import AccessError, InputError
import string

def clear_v1():
    data.clear()
    return {}

def search_v2(token, query_str):
    """
    Given a query string, return a collection of messages in all 
    of the channels/DMs that the user has joined that match the query

    Arguments:
        token (str) - the user's token
        query_str (str) - the string being searched
    
    Return Value:
        messages (list of dict) - each dictionary contains types: 
            - message_id
            - u_id, message
            - time_created
    """
    
    #data = getData()
    user_valid = False
    channel_list = []
    dm_list = []

    # Check if the query is more than 1000 characters
    if len(query_str) > 1000:
        raise InputError(description = 'Query string too long, invalid input')

    # Make the query string all one case to prevent case issues
    # Join the query string to make whitespace redundant
    query_str.lower()
    query_str.replace(' ', '')

    # Decode the token to access auth_user_id of the channel owner
    auth_user_id = find_user_id(token)

    for user in data['users']:
        if user.get('auth_user_id') is auth_user_id:
            user_valid = True
    # If the user is not a registered user, raise an inputerror
    if not user_valid:
        raise InputError(description = 'Token is invalid. Cannot search')

    # If there are no messages, raise an AccessError
    if data.get('messages') == None:
        raise AccessError(description = 'No messages in database')

    # Check the token belongs to a valid user
    #if user_valid:
    for user in data['users']:
        if user.get('auth_user_id') is auth_user_id:
        # Check if the user is a part of any channels or dms
            if user.get('channels_in') == None and user.get('dms_in') == None:
                raise AccessError(description = 'User does not belong to channel or dm. Cannot search')

    # Loop through and add all the messages with that channel Id and dm into 
    # a message list      
    for user in data['users']:
        if user.get('auth_user_id') is auth_user_id:
            if user.get('channels_in'):
                for channel in user['channels_in']:
                    channel_list.append(channel.get('channel_id'))
            if user.get('dms_in'):
                for dm in user['dms_in']:
                    dm_list.append(dm.get('dm_id'))
                    
    msg_list = []
    for message in data['messages']:
        # Get all the messages from the channel list
        # Loop through the whole list to see all the channels/dms the user is part of
        for chan_msg in channel_list:
            # If the message matches a channel the user is in, append the message to a msg_list
            if message.get('channel_id') is chan_msg:
                msg_list.append(message)
        # Get all the messages from the dm list
        for dm_msg in dm_list:
            if message.get('dm_id') is dm_msg:
                msg_list.append(message)

    matched_msgs = []
    # Compare the message value in each one of these message to the query_str
    for msg_check in msg_list:
        # Make the whitespace in messages redundant and remove whitespace in message
        temp_msg = msg_check.get('message').lower()
        # Check that the message has a word that matches the query_str
        found = check_search(temp_msg, query_str)
        if found:
            # Generate a dictionary of the matched message with the relevant information
            message_dict = {
                'message_id' : msg_check.get('message_index'),
                'u_id' : msg_check.get('sender'),
                'message' : msg_check.get('message'),
                'time_created' : msg_check.get('time_created'), 
                'reacts' :  msg_check.get('reacts'), 
                'is_pinned' : msg_check.get('is_pinned')
            }
            # Append this dictionary to the list of dictionaries to be returned
            matched_msgs.append(message_dict)

    # If there were no messages found, raise an InputError to say that no messages could be found
    if len(matched_msgs) == 0:
        raise InputError(description ='Unable to find any searches that match that query')


    return {
        'messages': matched_msgs
    }
