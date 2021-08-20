from src.data import getData
from src.error import InputError, AccessError
from src.helper import check_valid_info, check_members, find_user_id, get_timestamp, check_membership, check_msg_in, check_react, remove_react, react_check
from datetime import datetime
from datetime import timezone
import pytz

def message_send_v2(token, channel_id, message):
    """
    Send a message from authorised_user to the channel specified by channel_id.
    Note: Each message should have it's own unique ID.
    I.E. No messages should share an ID with another message,
    even if that other message is in a different channel.

    Arguments:
        token (str) - the user's token
        channel_id (int) - the channel's id
        message (str) - the message being sent
    
    Exceptions:
        InputError - Message is more than 1000 characters
        AccessError - the authorised user has not joined the channel they are trying to post to
    
    Return Value:
        message_id (int) - the message's id
    """
        # Create a list of dictionaries for messages if there is no existing message dictionary 
    data = getData()
    if data.get('messages') == None:
        data['messages'] = []

    in_channel = False
    channel_valid = False
    dream_user = False

    user_valid = False
    auth_user_id = find_user_id(token)
    # If token is invalid raise an Accesserror
    user_valid = check_valid_info(data["users"], auth_user_id)

    if user_valid == False:
        raise AccessError(description = 'User is not a registered user')

    # Check the message is not more than 1000 characters, else raise error
    if len(message) > 1000:
        raise InputError(description= 'Too many characters. Cannot send message')
    # Check that the channel is a valid ID
    channel_valid = check_valid_info(data['channels'], channel_id)
    
    if channel_valid is False:
        raise InputError(description= 'Channel ID invalid. Cannot send message')
    
    # Check that the user is a member of the channel they want to send a message to
    in_channel = check_members(data['channels'], auth_user_id)
    
    for users in data['users']:
        if users.get('auth_user_id') is auth_user_id:
            if users.get('global_permissions') == 1:
                dream_user = True


    # Loop through all the message indexes for this channel and add one for
    # this new message
    for msg in data["messages"]:
        if "channel_message_index" in msg:
            msg["channel_message_index"] += 1

    time_created = get_timestamp()
    # Generate the message dict

    if channel_valid is True and in_channel is True:
        new_message = {
            'message' : message,
            'message_id': len(data['messages'])+ 1,
            'reacts' : [],
            'sender' : auth_user_id,
            'channel_id' : channel_id,
            'message_index' : len(data['messages']) + 1, 
            'channel_message_index' : 0,
            'time_created' : time_created,
            'is_pinned' : False, 
        }
        data['messages'].append(new_message)
    
    # If the Dream owner is sending the message
    elif channel_valid is True and dream_user is True:
        new_message = {
            'message' : message,
            'message_id': len(data['messages']) + 1,
            'reacts' : [],
            'sender' : auth_user_id,
            'channel_id' : channel_id,
            'message_index' : len(data['messages']) + 1, 
            'channel_message_index' : 0,
            'time_created' : time_created,
            'is_pinned' : False, 
        }
        data['messages'].append(new_message)
     # If channel_valid and in_channel is false, raise AccessError
    else:
        raise AccessError('User not in channel or channel does not exist')

    print(len(data))
    # return message_index this in a dictionary
    return {
        'message_id': len(data['messages']),
    }

def message_remove_v1(token, message_id):
    """
    Given a message_id for a message, this message is removed from the channel/DM

    Arguments:
        token (str) - the user's token
        message_id (int) - the message's id
    
    Exceptions:
        InputError - Message (based on ID) no longer exists
        AccessError - Message with message_id was sent by the authorised user making this request
                    - The authorised user is an owner of this channel (if it was sent to a channel) or the **Dreams**

    Return Value:
        None
    """
    data = getData()
    user_valid = False
    auth_user_id = find_user_id(token)
    # If token is invalid raise an Accesserror
    user_valid = check_valid_info(data["users"], auth_user_id)

    if user_valid == False:
        raise AccessError(description = 'User is not a registered user')

    if data['messages'][message_id-1].get('message') == "This message has been removed": 
        raise InputError(description= "This message does not exist")

    sender = data["messages"][message_id-1].get("sender") #this returns the sender of the message 
    channel_id = data["messages"][message_id-1].get("channel_id")
    owners_list = data["channels"][channel_id-1].get("owner_members")
    
    dream_owner = False
    for users in data['users']:
        if users.get('auth_user_id') is auth_user_id: 
            if users.get('global_permissions') == 1:
                dream_owner = True 

    is_owner = False 
    for owners in owners_list: 
        if owners.get('u_id') is auth_user_id: 
            is_owner = True

    is_sender = False 
    if sender is auth_user_id: 
        is_sender = True 

    if not dream_owner and not is_sender and not is_owner: 
        raise AccessError(description= "You do not have the permissions to remove this message")

    for msg in data['messages']:
        if msg['message_id'] == message_id: 
            msg['message'] = "This message has been removed"

    return {
    }

def message_edit_v2(token, message_id, message): #remember, auth_user_id will actually be the token being taken in 
    """
    Given a message, update its text with new text.
    If the new message is an empty string, the message is deleted.

    Arguments:
        token (str) - the user's token
        message_id (int) - the message's id
        message (str) - the message being editted
    
    Exceptions:
        InputError - Length of message is over 1000 characters
        InputError - message_id refers to a deleted message
        AccessError - Message with message_id was sent by the authorised user making this request
                    - The authorised user is an owner of this channel (if it was sent to a channel) or the **Dreams**
    
    Return Value:
        None
    """
    data = getData()
    user_valid = False
    auth_user_id = find_user_id(token)
    # If token is invalid raise an Accesserror
    user_valid = check_valid_info(data["users"], auth_user_id)

    if user_valid == False:
        raise AccessError(description = 'User is not a registered user')

    if data['messages'][message_id-1].get('message') == "This message has been removed": 
        raise InputError(description = "This message has been removed")

    if len(message) > 1000: 
        raise InputError(description= 'Too many characters. Cannot send message')

    #access checks: perform checks to see if they have the permissions to edit the message 
    #need to check if the user calling message edit is an owner of the channel OR an owner of dreams 
    sender = data["messages"][message_id-1].get("sender") #this returns the sender of the message 
    channel_id = data["messages"][message_id-1].get("channel_id")
    owners_list = data["channels"][channel_id-1].get("owner_members")
    
    is_owner = False 
    for owners in owners_list: 
        if owners.get('u_id') is auth_user_id: 
            is_owner = True

    
    dream_owner = False
    for users in data['users']:
        if users.get('auth_user_id') is auth_user_id: 
            if users.get('global_permissions') == 1:
                dream_owner = True 
    
    is_sender = False 
    if sender is auth_user_id: 
        is_sender = True 
    
    if not dream_owner and not is_sender and not is_owner: 
        raise AccessError(description = "You do not have the permissions to edit this message")

    for messages in data["messages"]: 
        if messages.get("message_index") is message_id:
            if not message: 
                messages['message'] = "This message has been removed"
                break 
            #replace the current message with the message we want 
            else:
                messages["message"] = message
        
    return {
    }

def message_senddm_v1(token, dm_id, message):
    """
    Send a message from authorised_user to the DM specified by dm_id.
    Note: Each message should have it's own unique ID.
    I.E. No messages should share an ID with another message,
    even if that other message is in a different channel or DM.
    
    Arguments:
        token (str) - the user's token
        dm_id (int) - the dm's id
        message (str) - the message being sent
    
    Exceptions:
        InputError - Message is more than 1000 characters
        AccessError - the authorised user is not a member of the DM they are trying to post to
    
    Return Value:
        message_id (int) - the message's id
    """
    data = getData()
    
    user_valid = False
    auth_user_id = find_user_id(token)
    # If token is invalid raise an Accesserror
    user_valid = check_valid_info(data["users"], auth_user_id)

    if user_valid == False:
        raise AccessError(description = 'User is not a registered user')

    membs_list = []
    for membs in data["dm"][dm_id - 1]['all_members']:
        membs_list.append(membs["u_id"])
 
    if auth_user_id not in membs_list:
        raise AccessError(description = "Authorised user is not a member of the DM they are trying to post to") 
        
            
    if data.get('messages') == None:
        data['messages'] = []

    
    #raise input error 
    if len(message) > 1000:
        raise InputError(description= "Message is more than 1000 characters")
       
    message_id = len(data["messages"]) + 1

 
    for msg in data["messages"]:
        if "dm_message_index" in msg:
            msg["dm_message_index"] += 1
    
    time_created = get_timestamp()
    
    new_message_reg = { "message": message,
                        'message_id': len(data['messages']) + 1,
                        'reacts' : [],
                        "sender": auth_user_id,
                        'dm_id': dm_id,
                        'message_index': len(data['messages']) + 1,
                        "dm_message_index": 0,
                        'time_created' : time_created,  
                        'is_pinned': False,
                        }

    data["messages"].append(new_message_reg)
    
    return {
            'message_id': message_id,
    }
    

def message_share_v1(token, og_message_id, message, channel_id, dm_id):
    """
    'og_message_id' is the original message.
    'channel_id' is the channel that the message is being shared to, and is -1 if it is being sent to a DM.
    'dm_id' is the DM that the message is being shared to, and is -1 if it is being sent to a channel.
    'message' is the optional message in addition to the shared message,
    and will be an empty string '' if no message is given

    Arguments:
        token (str) - the user's token
        og_message_id (str) - the original message
        message (str) - the optional message
        channel_id (int) - the channel's id
        dm_id (int) - the dm's id
    
    Exceptions:
        AccessError - the authorised user has not joined the channel or DM they are trying to share the message to
    
    Return Value:
        shared_message_id (int) - the shared message's id
    """
    data = getData()

    user_valid = False
    auth_user_id = find_user_id(token)
    # If token is invalid raise an Accesserror
    user_valid = check_valid_info(data["users"], auth_user_id)

    if user_valid == False:
        raise AccessError(description = 'Invalid user')

    membs_list_channel = []
    membs_list_dm = []
        
    if data.get("share_message_id_counter") == None:
        data["share_message_id_counter"] = [1]
    
    shared_message_id = data["share_message_id_counter"][0]
     
    #raise input error 
    if len(message) > 1000:
        raise InputError(description = "Message is more than 1000 characters")

   
    #if bool(data):
    message_id = len(data["messages"]) + 1
  
    
    #find the message that corresponds to og_message_id
    for msg in data["messages"]:
        if msg["message_index"] == og_message_id:
            og_msg = msg["message"] 
    
    shared_message = message + " " + og_msg

    
    time_created = get_timestamp()
    
    #if sharing to a DM
    if channel_id == -1:

        #raising accesserror
        for key in data["dm"]:
            if key.get("dm_id") == dm_id:
                members_dict_list = key.get('all_members')
                for user in members_dict_list:
                    membs_list_dm.append(user["u_id"])
                if auth_user_id not in membs_list_dm:
                    raise AccessError(description= "The authorised user has not joined the dm they are trying to share the message to")

        
        for dm_msg in data["messages"]:
            if "dm_message_index" in dm_msg:
                dm_msg["dm_message_index"] += 1    
        
        msg_shared_dm_reg = { "message": shared_message,
                             'message_id': len(data['messages']) + 1,
                             'reacts' : [],
                             "sender": auth_user_id,
                             'dm_id': dm_id,
                             'message_index': message_id,
                             'shared_message_id': shared_message_id,
                             "dm_message_index": 0,
                             'time_created' : time_created }
        data["messages"].append(msg_shared_dm_reg)
        

        
    #if sharing to channel
    if dm_id == -1:
        
        #raising accesserror
        for membs in data["channels"][channel_id - 1]['all_members']:
            membs_list_channel.append(membs["u_id"])
            
        if auth_user_id not in membs_list_channel:
            raise AccessError(description = "The authorised user has not joined the channel they are trying to share the message to")   
        
        
        for chan_msg in data["messages"]:
            if "channel_message_index" in chan_msg:
                chan_msg["channel_message_index"] += 1
        
        msg_shared_channel_reg = { "message": shared_message,
                                   'message_id': len(data['messages']) + 1,
                                   'reacts' : [],
                                   "sender": auth_user_id,
                                   'channel_id': channel_id,
                                   'message_index': message_id,
                                   'shared_message_id': shared_message_id,
                                   "channel_message_index": 0,
                                   'time_created' : time_created }
            
        data["messages"].append(msg_shared_channel_reg )
    

    data["share_message_id_counter"][0] += 1

    return {'shared_message_id' : shared_message_id
    }    



def notifications_get_v1(token):
    """
    Returns the users most recent 20 notifications 

    Arguments:
        token (str) - the user's token
    
    Exceptions:
        N/A
    
    Return Value:
        notifications (list of dict) - each dictionary contains: 
            - channel_id, 
            - dm_id, 
            - notification_message
    """
    data = getData()
    user_valid = False
    adder = False
    joiner = False
    auth_user_id = find_user_id(token)
    # If token is invalid raise an Accesserror
    user_valid = check_valid_info(data["users"], auth_user_id)

    if user_valid == False:
        raise AccessError('User is not a registered user')

    user_handle = data["users"][auth_user_id - 1]["handle_str"]
    mentioned_handle = "@" + user_handle
    notifications = []
    
    
    if "channels" in data:
        for channel in data["channels"]:
            for membs in channel['all_members']:
                if auth_user_id == membs["u_id"] and auth_user_id != channel["creator"]:
                    #need to find out the adder of the token user
                    for reg in data["added_info"]["channels"]:
                        if reg["u_id"] == auth_user_id and reg["channel_id"] == channel["channel_id"]:
                            if reg.get('adder'):
                                adder_handle = reg["adder"]
                                adder = True
                            if reg.get('joiner'):
                                joiner_handle = reg['joiner']
                                joiner = True
                                
                    if adder:        
                        channel_name = channel["name"] 
                        
                        notification_added_channel = {"channel_id": channel["channel_id"],
                                                    "dm_id": -1,
                                                    "notification_message": f"{adder_handle} added you to {channel_name}"   
                                                    }  
                        notifications.append(notification_added_channel)  
                    if joiner:
                        channel_name = channel["name"] 
                    
                        notification_added_channel = {"channel_id": channel["channel_id"],
                                                    "dm_id": -1,
                                                    "notification_message": f"{joiner_handle} joined {channel_name}"   
                                                    }  
                        notifications.append(notification_added_channel)  
       
        
    if "dm" in data:
        for dm in data["dm"]:
            for membs in dm['all_members']:
                if auth_user_id == membs["u_id"] and auth_user_id != dm["creator"]:        
                    #need to find the adder of the token user
                    for reg in data["added_info"]["dms"]:
                        if reg["u_id"] == auth_user_id and reg["dm_id"] == dm["dm_id"]:
                            adder_handle = reg["adder"]
                                        
                    dm_name = dm["dm_name"]
                    
                    notification_added_dm = {"channel_id": -1,
                                             "dm_id": dm["dm_id"],
                                             "notification_message": f"{adder_handle} added you to {dm_name}"   
                                            }  
                    notifications.append(notification_added_dm)


    if "messages" in data:
        for msg in data["messages"]:
            #check every single message output and check if user was @userhandle was mentioned in any of those messages 
            if mentioned_handle in msg["message"]:
                if "dm_id" in msg:                                
                    dm_name = data["dm"][msg["dm_id"] - 1]["dm_name"]
                    sender_handle = data["users"][msg["sender"] - 1]["handle_str"]            
                    message = msg["message"]

                    notification_mentioned = {"channel_id": -1,
                                              "dm_id": msg["dm_id"],
                                              "notification_message": f"{sender_handle} tagged you in {dm_name} : {message[0:20]}"   
                                             }  
                    notifications.append(notification_mentioned)
                
                if "channel_id" in msg:
                    channel_name = data["channels"][msg["channel_id"] - 1]["name"]
                    sender_handle = data["users"][msg["sender"] - 1]["handle_str"] 
                    message = msg["message"]
                   
                    notification_mentioned = {"channel_id": msg["channel_id"],
                                              "dm_id": -1,
                                              "notification_message": f"{sender_handle} tagged you in {channel_name} : {message[0:20]}"   
                                             }
                    notifications.append(notification_mentioned)
            #check every single message output ahd check if there are reacts in that message
            #for msg in data["messages"]:
            if bool(msg["reacts"]) and msg["sender"] == auth_user_id: 
                #for reg_react in msg["reacts"]:
                    #if auth_user_id not in reg_react["u_ids"]:
                    #so far we have checked that IF there are reacts in a message
                if "dm_id" in msg: 
                    for reg in data["added_info"]["reacts"]:
                        #if someone has reacted to the user token
                        if reg["u_id"] == auth_user_id:
                            reactor_handle = reg["reactor"]
                            platform_name = reg["platform_name"]
                            notification_reacted = {"channel_id": -1,
                                                    "dm_id": msg["dm_id"],
                                                    "notification_message": f"{reactor_handle} reacted to your message in {platform_name}"   
                                                   }
                            notifications.append(notification_reacted)
                    
                if "channel_id" in msg:  
                    for reg in data["added_info"]["reacts"]:
                        if reg["u_id"] == auth_user_id:
                            #reacted message: "{User?s handle} reacted to your message in {channel/DM name}"
                            reactor_handle = reg["reactor"]
                            platform_name = reg["platform_name"]
                            notification_reacted = {"channel_id": msg["channel_id"],
                                                    "dm_id": -1,
                                                    "notification_message": f"{reactor_handle} reacted to your message in {platform_name}"   
                                                   }
                            notifications.append(notification_reacted)
                            
                            
                               
    
    
    
    
    notifications.reverse()
    
    final_output = []
    index = 0
    
    if len(notifications) <= 20:
        final_output = notifications
    else: #length would be >20 so need to output only first 20
        while index < 20:
            final_output.append(notifications[index])
            index += 1
        

    return { "notifications" : final_output
    }
    
def message_react_v1(token, message_id, react_id):
    """
    Adds a reaction from a user to a message 

    Arguments:
        token (str) - the valid user session id of the user that wants to unreact
        message_id (int) - the message the user wants to unreact to
        react_id (str) - the react id that the user wants to revoke

    Exceptions:
        InputError - message_id is not a valid message within a channel or DM that the authorised user has joined
        InputError - react_id is not a valid React ID. The only valid react ID the frontend has is 1
        InputError - Message with ID message_id already contains an active React with ID react_id from the authorised user
        AccessError - The authorised user is not a member of the channel or DM that the message is within
    
    Return Value:
        None
    """
   
    data = getData()
    auth_user_id = find_user_id(token)
    
    
    if auth_user_id == False:
        raise AccessError(description = "Invalid user")
    #input error if react id is invalid 
    react_valid = react_check(react_id)
    
    if not react_valid:
        raise InputError(description = 'React id is invalid')
    
    
    #input error if message is not a valid message id
    invalid_message = False
    for message in data["messages"]:
        if message["message_id"] == message_id:
            invalid_message = True
    
    if invalid_message == False:
        raise InputError(description = 'Message id is not a valid')
            
    
    #access error if user not in platform that message_id corresponds to
    in_platform = False
    
    if "dm_id" in data["messages"][message_id - 1]:
        dm_id = data["messages"][message_id - 1]["dm_id"]
        platform_name = data["dm"][dm_id - 1]["dm_name"]
        #check if user is a member of that dm
        for membs in data["dm"][dm_id - 1]['all_members']:
            if membs["u_id"] == auth_user_id:
                in_platform = True
  
    if "channel_id" in data["messages"][message_id - 1]:
        channel_id = data["messages"][message_id - 1]["channel_id"]
        platform_name = data["channels"][channel_id - 1]["name"]
        #check if user a member of that channel
        for membs in data["channels"][channel_id - 1]['all_members']:
            if membs["u_id"] == auth_user_id:
                in_platform = True        
        
    
    if in_platform == False:
        raise AccessError(description = 'User is not a member of the channel or dm that the message is in')
        
    
    
    #input error if Message with ID message_id already contains an active React with ID react_id from the authorised user 
    
    if bool(data["messages"][message_id - 1]["reacts"]):
        #if bool(data["messages"][message_id - 1]["reacts"][react_id - 1]):
            if auth_user_id in data["messages"][message_id - 1]["reacts"][react_id - 1]["u_ids"]:
                raise InputError(description = 'Already contains an active react from the authorised user' )
    
    sender = data["messages"][message_id - 1]["sender"]
    
       
    if sender == auth_user_id:    

        react_reg = { 'react_id': react_id,
                      'u_ids': [auth_user_id],
                      'is_this_user_reacted': True
                    }
    else:
    
        react_reg = { 'react_id': react_id,
                      'u_ids': [auth_user_id],
                      'is_this_user_reacted': False
                    }
    
                   

    if bool(data["messages"][message_id - 1]["reacts"]):
        for r in data["messages"][message_id - 1]["reacts"]:
            if r["react_id"] == react_id:
                r["u_ids"].append(auth_user_id)
                if sender == auth_user_id:
                    r['is_this_user_reacted'] = True
                
    else:
        #append a new react reg
        data["messages"][message_id - 1]["reacts"].append(react_reg)

    
 
        
    
    #THE FOLLOWING CODE IS TO SUPPORT THE NOTIFICIATIONS GET FUNCTION
    
    if sender is not auth_user_id:
        if data.get("added_info") == None:
            data["added_info"] = { }
        
        if data["added_info"].get("reacts") == None:
            data["added_info"]["reacts"] = []
        
        
        info_dict = {"u_id": data["messages"][message_id - 1]["sender"],
                     "platform_name" : platform_name,
                     "reactor" : data["users"][auth_user_id - 1]["handle_str"]
                    }
        data["added_info"]["reacts"].append(info_dict)
    return { } 



def message_unreact_v1(token, message_id, react_id):
    """
    Removes a reaction from a message the user had previously reacted to

    Arguments:
        token (str) - the valid user session id of the user that wants to unreact
        message_id (int) - the message the user wants to unreact to
        react_id (str) - the react id that the user wants to revoke

    Exceptions:
        InputError - message_id is not a valid message within a channel or DM that the authorised user has joined
        InputError - react_id is not a valid React ID
        InputError - Message with ID message_id does not contain an active React with ID react_id from the authorised user
        AccessError - The authorised user is not a member of the channel or DM that the message is within
    
    Return Value:
        None
    """
    data = getData()

    user_valid = False
    # Check that the user is a valid user
    auth_user_id = find_user_id(token)

    # Check that the react id is valid
    react_valid = react_check(react_id)

    if not react_valid:
        raise InputError(description= 'React invalid')

    user_valid = check_valid_info(data['users'], auth_user_id)
    if not user_valid:
        raise AccessError(description = 'User is not a valid member')

    # Check that the user is a part of channels or dms
    if check_membership(auth_user_id):
        # Find the channels and dms that the user is part of and add them to a list to sort through 
        if check_msg_in(auth_user_id, message_id):
            # If found then check react
            if check_react(auth_user_id, message_id, react_id):
                # If react found, remove react
                remove_react(auth_user_id, message_id, react_id)
            else:
                raise InputError(description = 'You have not reacted to this message')
        else:
            raise InputError(description = 'Message not found in your channels or dms')
    else:            
        raise AccessError(description= 'User is not a member of the channel or dm that the message is in')

    return {}

def message_pin_v1(token, message_id): 
    """
    Given a message within a channel or DM, remove it's mark as pinned

    Arguments: 
        token (str) - users unique session id 
        message_id (int) - id of the message to be pinned 

    Exceptions:
        InputError - message_id is not a valid message
        InputError - Message with ID message_id is already pinned
        AccessError - The authorised user is not a member of the channel or DM that the message is within
        AccessError - The authorised user is not an owner of the channel or DM
    
    Return Value: 
        None
    """
    data = getData()

    auth_user_id = find_user_id(token)

    if auth_user_id == False: 
        raise AccessError(description="This is not a valid user")

    message_id_valid = check_valid_info(data['messages'], message_id)
    if message_id_valid == False: 
        raise InputError(description= "This is not a valid message")

    for message in data["messages"]: 
        if message.get("message_id") == message_id: 
            if message.get("is_pinned") == True: 
                raise InputError(description= "This message is already pinned") 
    
    #get the channel or dm_id
    #first have to check if the message_id belongs to a dm or a channel by checking the keys of that data message dict 
    if "dm_id" in data["messages"][message_id - 1]: 
        dm_id = data["messages"][message_id - 1].get("dm_id")
        members_list = data["dm"][dm_id - 1]['all_members']
        creator =  data["dm"][dm_id - 1]["creator"]
        check_member = check_valid_info(members_list, auth_user_id)
        if creator != auth_user_id or check_member == False: 
            raise AccessError(description="You do not have the permissions to pin this message")

    if "channel_id" in data["messages"][message_id - 1]: 
        channel_id = data["messages"][message_id - 1].get("channel_id")
        members_list = data["channels"][channel_id - 1]['all_members']
        owners_list = data["channels"][channel_id - 1]["owner_members"]
        check_owner = check_valid_info(owners_list, auth_user_id)
        check_member = check_valid_info(members_list, auth_user_id)
        if check_owner == False or check_member == False: 
            raise AccessError(description="You do not have the permissions to pin this message")

    #if all input and access errors are bypassed, meaning everything is valid, pin the message
    for message in data["messages"]: 
        if message.get("message_id") == message_id: 
            message["is_pinned"] = True

    return {

    }    

def message_unpin_v1(token, message_id): 
    """
    Given a message within a channel or DM, remove it's mark as unpinned

    Arguments: 
        token (str) - users unique session id 
        message_id (int) - id of the message to be unpinned 

    Exceptions:
        InputError - message_id is not a valid message
        InputError - Message with ID message_id is already unpinned
        AccessError - The authorised user is not a member of the channel or DM that the message is within
        AccessError - The authorised user is not an owner of the channel or DM
    
    Return Value: 
        None
    """
    data = getData()

    auth_user_id = find_user_id(token)

    if auth_user_id == False: 
        raise AccessError(description="This is not a valid user")

    message_id_valid = check_valid_info(data['messages'], message_id)
    if message_id_valid == False: 
        raise InputError(description= "This is not a valid message")

    for message in data["messages"]: 
        if message.get("message_id") == message_id: 
            if message.get("is_pinned") == False: 
                raise InputError(description= "This message is already unpinned") 
    
    #get the channel or dm_id
    #first have to check if the message_id belongs to a dm or a channel by checking the keys of that data message dict 
    if "dm_id" in data["messages"][message_id - 1]: 
        dm_id = data["messages"][message_id - 1].get("dm_id")
        creator =  data["dm"][dm_id - 1]["creator"]
        if creator != auth_user_id: 
            raise AccessError(description="You do not have the permissions to unpin this message")

    if "channel_id" in data["messages"][message_id - 1]: 
        channel_id = data["messages"][message_id - 1].get("channel_id")
        owners_list = data["channels"][channel_id - 1]["owner_members"]
        check_owner = check_valid_info(owners_list, auth_user_id)
        if check_owner == False: 
            raise AccessError(description="You do not have the permissions to unpin this message")
    
    #if all input and access errors are bypassed, meaning everything is valid, unpin the message
    for message in data["messages"]: 
        if message.get("message_id") == message_id: 
            message["is_pinned"] = False

    return {

    }    

def message_sendlater_v1(token, channel_id, message, time_sent): 
    """
    Send a message from authorised_user to the channel specified by channel_id automatically at a specified time in the future

    Arguments:
        token (str) - users unique session id 
        channel_id (int) - the channel's id
        message (str) - the message being sent
        time_sent (int) - unix timestamp

    Exceptions:
        InputError - Channel ID is not a valid channel
        InputError - Message is more than 1000 characters
        InputError - Time sent is a time in the past
        AccessError - The authorised user has not joined the channel they are trying to post to

    Return Value:
        message_id (int) - the message's id
    """
    data = getData()
    empty_msgs = False
    auth_user_id = find_user_id(token)
    if auth_user_id == False: 
        raise AccessError(description= 'This is not a valid user')
    
    channel_valid = check_valid_info(data["channels"], channel_id)

    if channel_valid == False: 
        raise InputError(description= 'This is not a valid channel')
    
    # If token is invalid raise an Accesserror
    user_valid = check_valid_info(data["channels"][channel_id-1].get('all_members'), auth_user_id)

    if user_valid == False:
            raise AccessError(description='User is not apart of this channel')

    if len(message) > 1000:
        raise InputError(description="Message is more than 1000 characters")

    dt = datetime.now(pytz.timezone("GMT"))
    timestamp = dt.replace(tzinfo=timezone.utc).timestamp()

    if time_sent < timestamp: 
        raise InputError(description= "You cannot send a message to the past")

    #create an empty send_later dictionary to store the messages 
    if data.get("send_later") == None: 
        data["send_later"] = [] 

    if data.get("messages") == None: 
        data["messages"] = []
        empty_msgs = True

    new_reg = {
            "token" : token,
            "message": message, 
            "channel_id": channel_id,
            "time_sent": time_sent,  #time for it to be sent in the future 
    }
    data["send_later"].append(new_reg)
    #data["messages"].append({"message_id" : "id of message to be sent later"})
    if empty_msgs:
        message_id = 1
    else: 
        message_id = len(data['messages'])
    
    return {"message_id" : message_id}



def message_sendlaterdm_v1(token, dm_id, message, time_sent):
    """
    Send a message from authorised_user to the DM specified by dm_id automatically
    at a specified time in the future

    Arguments:
        token (str) - users unique session id
        dm_id (int) - the dm's id
        messsage (str) - the message being sent
        time_sent (int) - a time in the past
    
    Exceptions:
        InputError - DM ID is not a valid DM
        InputError - Message is more than 1000 characters
        InputError - Time sent is a time in the past
        AccessError - the authorised user is not a member of the DM they are trying to post to
    
    Return Value:
        message_id (int) - the message's id
    """

    data = getData()
    empty_msgs = False

    auth_user_id = find_user_id(token)
    if auth_user_id == False: 
        raise AccessError(description= 'This is not a valid user')
    #check if dm is valid
    dm_valid = check_valid_info(data["dm"], dm_id)

    #raise InputError if dm is invalid
    if dm_valid == False:
        raise InputError('dm is not valid')

    #check if user is valid
    user_valid = check_valid_info(data["dm"][dm_id-1].get('all_members'), auth_user_id)

    #raise AccessError is user is not valid
    if user_valid == False:
        raise AccessError(description = 'User is not valid')
    
    #raise InputError if message is more than 1000 characters
    if len(message) > 1000:
        raise InputError(description = "Message is more than 1000 characters")

    dt = datetime.now(pytz.timezone("GMT"))
    timestamp = dt.replace(tzinfo=timezone.utc).timestamp()

    #raise InputError if message is sent in the past
    if time_sent < timestamp: 
        raise InputError(description = "You cannot send a message to the past")

    #create an empty send_later dictionary to store the messages 
    if data.get("send_later") == None: 
        data["send_later"] = [] 

    if data.get("messages") == None: 
        data["messages"] = []
        empty_msgs = True

    new_reg = {
            "token" : token,
            "message": message, 
            "dm_id": dm_id,
            "time_sent": time_sent,  #time for it to be sent in the future 
    }
    data["send_later"].append(new_reg)
    #data["messages"].append({"message_id" : "id of message to be sent later"})
    if empty_msgs:
        message_id = 1
    else: 
        message_id = len(data['messages'])
    return {
            'message_id': message_id,
    }
