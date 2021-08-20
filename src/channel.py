from src.data import getData
from src.error import AccessError, InputError
from src.helper import check_valid_info, check_members, add_to_channel_member_list,  join_channel, find_user_id
from src.helper import get_timestamp

def channel_invite_v2(token, channel_id, u_id):
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
    data = getData()
    # Decode the token to access auth_user_id of the channel owner
    auth_user_id = find_user_id(token)
    # Set the following as false to be checked before implementing feature
    user_valid = False
    channel_valid = False
    auth_user_valid = False
    auth_is_user = False
    
    # Ensure there is a channels key if the wrong input is sent in
    if data.get('channels') == None:
        data['channels'] = []

    # Only run code if there is information in data
    # Checks both u_id and auth_user_id are existing users
    # Check the channel id exists
    user_valid = check_valid_info(data['users'], u_id)
    auth_user_valid = check_valid_info(data['users'], auth_user_id)

    # If user id not found, raise exception
    if user_valid == False:
        raise InputError(description= "User ID does not exist")
    
    if auth_user_valid == False:
        raise InputError(description= 'User ID does not exist')

    channel_valid = check_valid_info(data['channels'], channel_id)
    # If channel id not found, raise exception
    if channel_valid == False:
        raise InputError(description= "Channel ID does not exist")
        
    # Check that the user wanting to add u_id is a member of the channel
    auth_is_user = check_members(data['channels'], auth_user_id)
    # If yes, then append the user as a channel member
    if auth_is_user:
        add_to_channel_member_list(u_id, channel_id)
    # If they are not a member, raise AccessError
    else: 
        raise AccessError(description= "You are not a member of this channel. You do not have permission to add users to this channel")

    #THE FOLLOWING CODE IS TO SUPPORT NOTIFICATIONS_GET FUNCTION  
    if data.get("added_info") == None:
        data["added_info"] = { }
    
    if data["added_info"].get("channels") == None:
        data["added_info"]["channels"] = []
    
    info_dict = {"u_id": u_id,
                 "channel_id" : channel_id,
                 "adder" : data["users"][auth_user_id - 1]["handle_str"]
                }
    data["added_info"]["channels"].append(info_dict)
       
    return {
    }      

def channel_details_v2(token, channel_id):
    """
    Given a Channel with ID channel_id that the authorised user is part of, provide basic details about the channel

    Arguments:
        token (str) - the user's token
        channel_id (int) - the channel's id
    
    Exceptions:
        InputError - Channel ID is not a valid channel
        AccessError - Authorised user is not a member of channel with channel_id
    
    Return Value:
        dictionary consisting of a 
            string: name, 
            int: is public, 
            list: owner members 
            list: all members
    """

    data = getData()

    # Decode the token to access auth_user_id of the channel owner
    auth_user_id = find_user_id(token)

    # If token passed in is None or invalid
    if auth_user_id is False:
        raise AccessError(description = 'Invalid token')
    
    #input error: occurs when channel id is not valid 
    #Check channel id is a valid channel, call check_channel_valid
    channel_valid = False

    # Ensure that there is a channels key if wrong input is passed through to assure an InputError is raised
    if data.get('channels') == None:
        data['channels'] = []

    # Ensure that channel_id and start is an int if passed through a get request
    if channel_id == None:
        raise InputError(description = 'Invalid input')

    # Ensure that channel_id is an int if passed through a get request
    channel_id = int(channel_id)
    channel_valid = check_valid_info(data['channels'], channel_id)

    if channel_valid == False:
        raise InputError(description = 'Channel ID is not a valid channel')   


    #check if user is a member of the channel
    memb_found = False 
    for memb in data["channels"][channel_id - 1]['all_members']:
        if memb["u_id"] == auth_user_id:
            memb_found = True
            
    if memb_found == False:
        raise AccessError(description = 'User is not a member of channel with this channel id')     
     
    #finding name of the channel using channel id:
    name = data["channels"][channel_id - 1].get("name")

    member_list = data["channels"][channel_id - 1]['all_members']
    owner_list = data["channels"][channel_id - 1]["owner_members"]
                    
    privacy_status = data["channels"][channel_id - 1]["is_public"]

    return {   
                'name': name,
                'is_public': privacy_status,
                'owner_members': owner_list,
                'all_members' : member_list
           }          

def channel_messages_v2(token, channel_id, start):
    """
    Given a Channel with ID channel_id that the authorised user is part of,
    return up to 50 messages between index "start" and "start + 50".
    Message with index 0 is the most recent message in the channel.
    This function returns a new index "end" which is the value of "start + 50", or,
    if this function has returned the least recent messages in the channel,
    returns -1 in "end" to indicate there are no more messages to load after this return.

    Arguments:
        token (str) - the user's token
        channel_id (int) - the channel's id
        start (int) - the starting index
    
    Exceptions:
        InputError - Channel ID is not a valid channel
        InputError - start is greater than the total number of messages in the channel
        AccessError - Authorised user is not a member of channel with channel_id
    
    Return Value:
        messages (dict) - consists of a string: message_id, u_id, message, time_created
        start (int) - the starting index
        end (int) - the last index
    """
    data = getData()
    # Check if inputs are valid
    user_valid = False
    channel_valid = False
    is_member = False
    end = -1

    # Ensure there is a channels key if an invalid key is passed in when no channels exist
    if data.get('channels') == None:
        data['channels'] = []

    # Get auth_user_id from the token
    auth_user_id = find_user_id(token)
    # Check if user is a valid token
    user_valid = check_valid_info(data['users'], auth_user_id)
    # If the auth_user_id is not found, token invalid
    if auth_user_id == False or user_valid == False:
        raise AccessError(description= 'Token invalid')

    # Ensure that channel_id and start is an int if passed through a get request
    if channel_id == None:
        raise InputError(description= 'Invalid input')

    channel_id = int(channel_id)
    start = int(start)

    channel_valid = check_valid_info(data['channels'], channel_id)
    is_member = check_members(data['channels'], auth_user_id)
    # Raise InputError if Id does not exist
    if channel_valid == False:
        raise InputError(description= 'User or channel ID does not exist')
    # Raise AccessError if user is not member of the channel
    elif is_member == False:
        raise AccessError(description= 'User is not member of channel. Denied Access to messages')
    
    # Create a list that the messages will be appended to to return to the user
    message_list = []
    if data.get('messages') == None:
        data['messages'] = []

    # Get the length of the messages in the channel
    length = 0
    all_channel_messages = []
    # Get all the messages under the channel id
    if len(data['messages']) > 0:
        for msg in data['messages']:
            if msg.get('channel_id') == channel_id:
                all_channel_messages.append(msg)
            length = len(all_channel_messages)

    if length < start:
        raise InputError(description= 'Start is greater than the total messages')

    j = 0
    if length < 50: # if messages is less than 50
        while j < length: 
            message_dict = {
                'message_id' : all_channel_messages[j].get('message_id'), 
                'u_id' : all_channel_messages[j].get('sender'),
                'message' : all_channel_messages[j].get('message'),
                'time_created' :  all_channel_messages[j].get('time_created'),
                'reacts' : all_channel_messages[j].get('reacts'),
                'is_pinned' : all_channel_messages[j].get('is_pinned')
            }
            
            message_list.append(message_dict)
            j += 1
              
    else:    
        i = start
        while i < (start + 50): # for cases with greater than 50 messages
            message_dict = {
                'message_id' : all_channel_messages[i].get('message_id'), 
                'u_id' : all_channel_messages[i].get('sender'),
                'message' : all_channel_messages[i].get('message'),
                'time_created' :  all_channel_messages[i].get('time_created'),
                'reacts' : all_channel_messages[i].get('reacts'),
                'is_pinned' : all_channel_messages[i].get('is_pinned')
            }
            
            message_list.append(message_dict)
            i += 1
            end = start + 50
    
    message_list.reverse()
    return {'messages' : message_list, 'start' : start, 'end' : end}

def channel_leave_v1(token, channel_id):
    """
    Given a channel ID, the user removed as a member of this channel.
    Their messages should remain in the channel

    Arguments:
        token (str) - the user's token
        channel_id (int) - the channel's id
    
    Exceptions:
        InputError - Channel ID is not a valid channel
        AccessError - Authorised user is not a member of channel with channel_id
    
    Return Value:
        None
    """
    data = getData()
    auth_user_id = find_user_id(token)

    if auth_user_id == False: 
        raise AccessError(description = "This user id is not valid")

    # Ensure there is a channels key if an invalid key is passed in when no channels exist
    if data.get('channels') == None:
        data['channels'] = []

    member_valid = False

    #check that auth_user_id and channel_id exist
    channel_valid = check_valid_info(data['channels'], channel_id)

    #if channel_id is invalid
    if channel_valid == False:
        raise InputError(description= "This channel ID does not exist")

    members_list = data['channels'][channel_id - 1]['all_members']
    owners_list = data['channels'][channel_id-1]['owner_members']
    #check that auth_user_id is a member of the channel
    for members in members_list:
        if members.get('u_id') is auth_user_id:
            member_valid = True
    
    if not member_valid:
        raise AccessError(description= "User is not a member")
    i = 0
    #delete user as a member
    for member in members_list:
        if member.get('u_id') == auth_user_id:
            del members_list[i]
        i+= 1
    # delete user as an owner
    j = 0
    for owner in owners_list:
        if owner.get('u_id') == auth_user_id:
            del owners_list[j]
        j += 0

    if len(data['channels'][channel_id - 1]['all_members']) == 0: 
        data["channels"][channel_id -1]["channel_id"] = "This channel has been removed"
        data["channels"][channel_id -1]["name"] = "This channel has been removed"
        data["channels"][channel_id -1]["creator"] = "This channel has been removed"

    return {
    }

def channel_join_v2(token, channel_id):
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
    data = getData()
    user_valid = False
    channel_valid = False
    dreams_owner = False

    # Ensure there is a channels key if an invalid key is passed in when no channels exist
    if data.get('channels') == None:
        data['channels'] = []

    # Decode the token to access auth_user_id of the channel owner
    auth_user_id = find_user_id(token)

    #Check if Dreams owner
    if data['users'][auth_user_id - 1].get('global_permissions') == 1:
        dreams_owner = True

    # Only check data if dictionary had information stored
    # Check that auth_user_id and channel_id exist
    if bool(data['channels']):
        user_valid = check_valid_info(data['users'], auth_user_id)
        channel_valid = check_valid_info(data['channels'], channel_id)
        
    if user_valid == False or channel_valid == False:
        raise InputError(description= "User and/or channel ID does not exist")
    
    # If the channel is private check the user was invited to join the channel
    if data['channels'][channel_id - 1].get('is_public') == False:
        if dreams_owner:
            join_channel(auth_user_id, channel_id)
        else:
            raise AccessError(description='Cannot join a private channel')
    
    # If the channel is public or is a dreams owner add them to the channel
    if data['channels'][channel_id - 1].get('is_public'):
        join_channel(auth_user_id, channel_id)
    
    
    if data.get("added_info") == None:
        data["added_info"] = { }
    
    if data["added_info"].get("channels") == None:
        data["added_info"]["channels"] = []
    
    info_dict = {"u_id": auth_user_id,
                 "channel_id" : channel_id,
                 "joiner" : data["users"][auth_user_id - 1]["handle_str"]
                }
    data["added_info"]["channels"].append(info_dict)
   
          
    return {
    }

def channel_addowner_v1(token, channel_id, u_id):
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
    data = getData()
    auth_user_valid = False
    user_valid = False
    channel_valid = False
    owner_valid = False
    dream_user = False

    # Ensure there is a channels key if an invalid key is passed in when no channels exist
    if data.get('channels') == None:
        data['channels'] = []

    # Decode the token to access auth_user_id of the channel owner
    auth_user_id = find_user_id(token)

    # Check if the ID's passed through are valid
    user_valid = check_valid_info(data['users'], u_id)
    auth_user_valid = check_valid_info(data['users'], auth_user_id)
    channel_valid = check_valid_info(data['channels'], channel_id)
    
    # ID's are not valid, raise InputError
    if auth_user_valid == False or user_valid == False or channel_valid == False:
        raise InputError(description= 'User or channel ID is not valid')

    # Check if the user is a **Dreams** Owner
    for users in data['users']:
        if users.get('auth_user_id') == auth_user_id:
            if users.get('global_permissions') == 1:
                dream_user = True

    # Loop to see if auth_user is an owner of the channel
    for key in data['channels']:
        for owner in key.get('owner_members'):
            if owner.get('u_id') is auth_user_id:
                owner_valid = True    

    # If the owner was not found and the user is not a Dream's Owner raise AccessError
    if owner_valid == False and dream_user == False:
        raise AccessError(description= 'User is not an owner of this channel. Cannot add user as owner')

    # Generate the member info for the owner that is going to be added to the owner list
    for user in data['users']:
        if user.get('auth_user_id') == u_id:
            user_info = {
                'u_id' : u_id,
                'email' : user.get('email'),
                'name_first' : user.get('f_name'),
                'name_last' : user.get('l_name'),
                'time_created' : get_timestamp(),
                'handle_str' : user.get('handle_str'),
                'profile_img_url' : user.get('profile_img_url')
            }

    # Loop through the channels in data['channels']        
    for channel in data['channels']:
        # Read each key and value in channel
        for key, val in channel.items():
            if key == 'owner_members':
                # Check if the u_id is an existing owner of the channel
                for owner_check in val:
                    if owner_check.get('u_id') == u_id:
                        raise AccessError('Already an owner of this channel')
                # Append the user to the channel
                val.append(user_info)

    return {
    }

def channel_removeowner_v1(token, channel_id, u_id):
    """
    Remove user with user id u_id an owner of this channel

    Arguments:
        token (str) - the user's token that is requesting
        channel_id (int) - the channel's id
        u_id (int) - the user's id that is being changed
    
    Exceptions:
        InputError - Channel ID is not a valid channel
        InputError - When user with user id u_id is not an owner of the channel
        InputError - The user is currently the only owner
        AccessError - the authorised user is not an owner of the **Dreams**, or an owner of this channel
    
    Return:
        None
    """
    data = getData()
    auth_user_id = find_user_id(token)
    dreams_owner = False
    auth_owner_valid = False
    uid_owner_valid = False
    dreams_user = False

    # Ensure there is a channels key if an invalid key is passed in when no channels exist
    if data.get('channels') == None:
        data['channels'] = []

    #check that auth_user_id and channel_id exist
    uid_valid = check_valid_info(data['users'], u_id)
    auth_user_id_valid = check_valid_info(data['users'], auth_user_id)
    channel_valid = check_valid_info(data['channels'], channel_id)

    #if user_id or channel_id is invalid
    if uid_valid == False or channel_valid == False or auth_user_id_valid == False:
        raise InputError("User and/or channel ID does not exist")

    #may need to change later
    dreams_owner = data['users'][auth_user_id - 1]['global_permissions']
    owners_list = data['channels'][channel_id - 1]['owner_members']

    # Check if the user is a **Dreams** Owner
    if dreams_owner == 1:
        dreams_user = True

    #check that auth_user_id is an owner of the channel
    for owner in owners_list:
        if owner.get('u_id') == auth_user_id:
            auth_owner_valid = True

    #check that u_id is an owner of the channel
    for owner in owners_list:
        if owner.get('u_id') == u_id:
            uid_owner_valid = True

    #input error if u_id is not an owner
    if not uid_owner_valid:
        raise InputError("U_id is not an owner")

    #input error if there is only one owner
    if len(owners_list) == 1:
        raise InputError("Only one owner")

    #access error if auth_user_id is not an owner of the channel nor a dreams owner
    if not auth_owner_valid and not dreams_user:
        raise AccessError("User is not an owner")

    #remove ownership from user
    i = 0
    for owner in owners_list:
        if owners_list[i].get('u_id') == u_id: 
            del owners_list[i]
        i += 1

    return {
    }
