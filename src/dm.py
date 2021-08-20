from src.data import getData 
from src.error import AccessError, InputError   
from src.helper import check_valid_info, find_user_id, get_user_info, check_members, get_timestamp
from datetime import datetime

def dm_details_v1(token, dm_id):
    """
    Users that are part of this direct message can view basic information about the DM

    Arguments: 
        token (str) - the user's token
        dm_id (int) - the dm's id
    
    Exceptions:
        InputError - DM ID is not a valid DM
        AccessError - Authorised user is not a member of this DM with dm_id
    
    Return Value: 
        name (str) - the dm's name
        members (list of dict) - each dictionary contains types: user
    """

    data = getData()
    auth_user_id = find_user_id(token)
    
    if auth_user_id == False: 
        raise AccessError(description= 'This is not a valid user')
    
    # Ensure that there is a dms key if wrong input is passed through to assure an InputError is raised
    if data.get('dm') == None:
        data['dm'] = []

    if dm_id == None:
        raise InputError('Invalid input')
    dm_id = int(dm_id)
    
    if not check_valid_info(data['dm'], dm_id): 
        raise InputError(description = "This dm_id does not exist")
    dm_name = data['dm'][dm_id - 1]['dm_name']
    members_list = data['dm'][dm_id - 1]['all_members']
     
    
    
    valid = check_valid_info(members_list, auth_user_id)

    if valid is False:
        raise AccessError(description = "This user is not apart of this DM")

    dm_dict = {"name" : dm_name, "members": members_list}
    return dm_dict

def dm_list_v1(token):
    """
    Returns the list of DMs that the user is a member of

    Arguments: 
        token (str) - the user's token
    
    Exceptions:
        N/A
    
    Return Value:
        dms (list of dict) - each dictionary contains types: dm_id, name
    """

    data = getData()
    dm_dict = {}

    # If the dm list is empty
    if data.get('dm') == None:
        data['dm'] = []
    
    
    auth_user_id = find_user_id(token)
    
    if auth_user_id == False: 
        raise AccessError(description= 'This is not a valid user')

    dms_user_list = {"dms" : []}

    for dms in data['dm']:
            for key, val in dms.items(): #this line will access each key in each dict
                if key == 'all_members': #checks if the variable is valid 
                    for user_dict in val:
                        if user_dict.get("u_id") == auth_user_id:
                            dm_dict = {"dm_id" : dms['dm_id'], "name" : dms["dm_name"]} 
                            dms_user_list['dms'].append(dm_dict)

    return dms_user_list
    
def dm_create_v1(token, u_ids):
    """
    [u_id] is the user(s) that this DM is directed to. name should be automatically generated based
    on the user(s) that is in this dm. The name should be an alphabetically-sorted,
    comma-separated list of user handles, e.g. 'handle1, handle2, handle3'.

    Arguments: 
        token (str) - the user's token
        u_ids (list) - list of u_ids
    
    Exceptions:
        InputError - u_id does not refer to a valid user
    
    Return Value:
        dm_id (int) - the dm's id
        dm_name (str) - the dm's name
    """

    data = getData()
    auth_user_id = find_user_id(token)
    
    if auth_user_id == False: 
        raise AccessError(description= 'This is not a valid user')

    u_ids.sort()
    
    if data.get("dm") == None:
        data["dm"] = []
    
    #checking if input is valid ie. checking if u_id refers to a valid user 
    #u_id is going to be a list of users, we must check that these user id's exist in the data["users"] dict
    
    user_listx = []
    for user in data["users"]:
        user_listx.append(user["auth_user_id"])
    #new code
    for ids in u_ids:
        if ids not in user_listx:
            # This isn't getting run
            raise InputError(description = 'User id(s) does not refer to a valid user')
    
    dm_id = len(data["dm"]) + 1

    #finding names of the user ids and putting them into a string in alphabetical order and correct format
    handles_list = []
    #old code
    for user in data["users"]:
        for ids in u_ids: 
            if user["auth_user_id"] is ids: 
                handles_list.append(user["handle_str"])
        if user["auth_user_id"] is auth_user_id:
            handles_list.append(user["handle_str"])


    handles_list.sort()
    
    handles_string = ", "
    
    finalised_handle = handles_string.join(handles_list)
        
    #what we need to do here is to create a members list and append a dictionary containing some "detailing" info into there 
    members_list = []
    
    i = 0
    while i<len(data["users"]): 
        user_id = data["users"][i].get("auth_user_id")
        if user_id == auth_user_id:     
            dictionary = {
                "u_id": auth_user_id,
                "email": data["users"][i].get('email'),
                "name_first": data["users"][i].get('f_name'),
                "name_last": data["users"][i].get('l_name'), 
                "handle_str" : data['users'][i].get('handle_str'),
                "profile_img_url" : data['users'][i].get('profile_img_url')
                }
            members_list.append(dictionary)
            i = len(data["users"])
        else: 
            i += 1
    
    #what we need to do here is to create a members list and append a dictionary containing some "type user" info there 
    #new code
    for i in range(len(u_ids)):
        
        dictionary = {
            "u_id": u_ids[i],
            "email": data["users"][u_ids[i]-1].get('email'),
            "name_first": data["users"][u_ids[i]-1].get('f_name'),
            "name_last": data["users"][u_ids[i]-1].get('l_name'),
            "handle_str" : data['users'][u_ids[i]-1].get('handle_str'),
            "profile_img_url" : data['users'][u_ids[i]-1].get('profile_img_url')
        }
            
        members_list.append(dictionary)
    
    new_dm_reg = { 
        "dm_id": dm_id,
        "dm_name": finalised_handle,
        "creator": auth_user_id,
        'all_members': members_list,
        'time_created' : get_timestamp(),
        }
    
    # Generate timestamp for time user joined the dm, add this to a dict to add to dms_in
    time_stamp = get_timestamp()
    dm_info = {
        'dm_id' : dm_id,
        'time_stamp' : time_stamp,
    }
    # Append the user to the dm dictionary and add this dm to the user's dm membership key in 
    
    for person in data['users']:
        for member in members_list:
            if person.get('auth_user_id') == member.get('u_id'):
                if person.get('dms_in') == None:
                    person['dms_in'] = []
                person.get('dms_in').append(dm_info)

    #if bool(data):
    data["dm"].append(new_dm_reg)
        
    #FOLLOWIJNG IS FOR NOTIFICATIONS GET FUNCTION / ALI
    if data.get("added_info") == None:
        data["added_info"] = { }
    
    if data["added_info"].get("dms") == None:
        data["added_info"]["dms"] = []
    
    for user_id in u_ids:
        info_dict = {
            "u_id": user_id,
            "dm_id" : dm_id,
            "adder" : data["users"][auth_user_id - 1]["handle_str"]
            }
        data["added_info"]["dms"].append(info_dict)    

    print(type(finalised_handle))
    return  { 
        "dm_id" : dm_id, 
        "dm_name" : finalised_handle
    } 

def dm_remove_v1(token, dm_id): 
    """
    Remove an existing DM. This can only be done by the original creator of the DM.

    Arguments: 
        token (str) - the user's token
        dm_id (int) - the dm's id
    
    Exceptions:
        InputError - dm_id does not refer to a valid DM
        AccessError - the user is not the original DM creator
    
    Return Value:
        None
    """

    data = getData()
    auth_user_id = find_user_id(token)
    if auth_user_id == False: 
        raise AccessError(description= 'This is not a valid user')

    dm_valid = False 
    dm_valid = check_valid_info(data["dm"], dm_id) 

    if dm_valid is False: 
        raise InputError(description ="This dm_id does not refer to a valid DM ")

    creator = False
    for dm in data["dm"]: 
        if dm.get("dm_id") == dm_id:
            if dm.get("creator") == auth_user_id: 
                creator = True 
                
    if creator is False: 
        raise AccessError(description = "You are not the creator of the dm and do not have permission to remove it")

    i = 0
    for dm in data['dm']:
        if data["dm"][i]['dm_id'] == dm_id: 
            data["dm"][i]['dm_name'] = "This dm has been removed"
            data["dm"][i]['dm_id'] = "This dm has been removed"
            del data["dm"][i]['all_members'] 
        i += 1
    
    if data.get('messages') == None:
        data['messages'] = []

    for msg in data['messages']:
        if msg.get('dm_id') == dm_id: 
            msg['message'] = "This dm has been removed"

    return {

    }

def dm_invite_v1(token, dm_id, u_id): 
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

    data = getData()
    dm_valid = False
    user_valid = False
    is_member = False
    token_valid = False

    # Check if the dm_id is valid
    dm_valid = check_valid_info(data['dm'], dm_id)
   
    # Check if the u_id to be invited is valid
    user_valid = check_valid_info(data['users'], u_id)

    if dm_valid is False or user_valid is False:
        raise InputError(description = 'Cannot invite, DM/User does not exist')
    
    # Decode the token to get the user inviting to dm
    dm_member = find_user_id(token)

    # Check if u_id is already a member of the dm
    # Else add the user to the dm member list
    for key in data['dm']:
        # Find the member key in dm
        if key.get('dm_id') is dm_id:
            for member_dict in key.get('all_members'):
                if member_dict.get('u_id') is u_id:
                    is_member = True
                elif member_dict.get('u_id') is dm_member:
                    token_valid = True
    
    if token_valid is False:
        raise InputError(description ='Invalid user, cannot invite')

    # Concatenate the invited user to the handle name and add this to the dm dictionary
    members_list = []
    for key in data['dm']:
        if key.get('dm_id') is dm_id:
            for member in key.get('all_members'):
                members_list.append(member)
    
    handles_list = []
    for user in data["users"]:
        for ids in members_list: 
            if user.get("auth_user_id") is ids.get('u_id'): 
                handles_list.append(user["handle_str"])
        if user.get("auth_user_id") is u_id: 
            handles_list.append(user["handle_str"])

    handles_list.sort()
    
    handles_string = ", "
    
    finalised_handle = handles_string.join(handles_list)

    # If the user is not a member of the dm, append them to the members list
    # If the user is part of the dm, raise AccessError
    if is_member is False:
        user_info = get_user_info(u_id)
        for dm in data['dm']:
            if dm.get('dm_id') is dm_id:
                dm.get('all_members').append(user_info)
                dm['dm_name'] = finalised_handle
    else:
        raise AccessError(description = 'User is already a member of this DM')

    # Generate timestamp for time user joined the dm, add this to a dict to add to dms_in
    time_stamp = get_timestamp()
    dm_info = {
        'dm_id' : dm_id,
        'time_stamp' : time_stamp,
    }
    # Append the user to the dm dictionary and add this dm to the user's dm membership key in 
    # data['users']
    for person in data['users']:
        if person.get('auth_user_id') is u_id:
            if person.get('dms_in') == None:
                person['dms_in'] = []
            person.get('dms_in').append(dm_info)
    
    info_dict = {"u_id": u_id,
                 "dm_id" : dm_id,
                 "adder" : data["users"][dm_member - 1]["handle_str"]
                }
    data["added_info"]["dms"].append(info_dict)  

    
    return {
    }

def dm_leave_v1(token, dm_id):
    """
    Given a DM ID, the user is removed as a member of this DM

    Arguments:
        token (str) - the user's token
        dm_id (int) - the dm's id
    
    Exceptions:
        InputError - dm_id is not a valid DM
        AccessError - Authorised user is not a member of DM with dm_id
    
    Return Value:
        None
    """

    data = getData()
    auth_user_id = find_user_id(token)

    member_valid = False

    #check that auth_user_id and dm_id are valid
    user_valid = check_valid_info(data['users'], auth_user_id)
    dm_valid = check_valid_info(data['dm'], dm_id)

    #if user_id or channel_id is invalid
    if user_valid == False or dm_valid == False:
        raise InputError(description = "User and/or dm ID does not exist")
    
    members_list = data['dm'][dm_id - 1]['all_members']

    #check that auth_user_id is a member of the channel
    for members in members_list:
        if members.get('u_id') is auth_user_id:
            member_valid = True
    
    if not member_valid:
        raise AccessError(description = "User is not a member")
    
    #delete user as a member
    #if user_valid:
    i = 0
    for member in members_list:
        #for i in range(len(members_list)):
            if member.get('u_id') == auth_user_id:
                del members_list[i]
            i += 1
    
    #need to revert the name of the dm such that it does not include the person that has left the dm
    #do this by generating the dm_name in the absence of the user in memberslist
    #finding names of the user ids and putting them into a string in alphabetical order and correct format
    
    #to generate dm name, get the handles of all of the members, append them to a list, then sort that list, then do blah..
    handle_list = []
    user_id_list = []
    for membs in data["dm"][dm_id - 1]["all_members"]:
        user_id_list.append(membs["u_id"])
    
    for ids in user_id_list:
        handle_list.append(data["users"][ids - 1]["handle_str"])
    
    handle_list.sort()
    
    handles_string = ", "
    
    new_handle = handles_string.join(handle_list) 
    
    data["dm"][dm_id - 1]["dm_name"] = new_handle
    
    
    return {
    }

def dm_messages_v1(token, dm_id, start):
    """
    Given a DM with ID dm_id that the authorised user is part of, return up to 50 messages between index 
    "start" and "start + 50". Message with index 0 is the most recent message in the dm. 
    This function returns a new index "end" which is the value of "start + 50", or, if this function has 
    returned the least recent messages in the dm, returns -1 in "end" to indicate there are 
    no more messages to load after this return.

    Arguments: 
        token (str) - the user's token
        dm_id (int) - the dm's id
        start (int) - the starting index
    
    Exceptions:
        InputError - DM ID is not a valid DM
        InputError - start is greater than the total number of messages in the channel
        AccessError - Authorised user is not a member of DM with dm_id
    
    Return Value: 
        messages (list of dict) - each dictionary contains types: message_id, u_id, message, time_created
        start (int) - the starting index
        end (int) - the last index
    """
    data = getData()
    # Check if inputs are valid
  
    dm_valid = False
    is_member = False
    end = -1

    # Get auth_user_id from the token
    auth_user_id = find_user_id(token)

    if auth_user_id == False: 
        raise AccessError(description= 'This is not a valid user')

    # Ensure that dm_id and start are int values when passed through server
    dm_id = int(dm_id)
    start = int(start)
    
    dm_valid = check_valid_info(data['dm'], dm_id)
    is_member = check_members(data['dm'], auth_user_id)
    
    # Raise InputError if Id does not exist
    if dm_valid is False:
        raise InputError(description = 'Dm ID does not exist')
    # Raise AccessError if user is not member of the dm
    if is_member is False:
        raise AccessError(description = 'User is not member of the dm. Denied Access to messages')

    message_list = []

    # If there are no messages, raise an access error
    # Removed the access error to align with front end
    if data.get('messages') == None:
        data['messages'] = []
        
    # Get the length of the messages in the dm
    length = 0
    all_dm_messages = []
    # Get all the messages under the dm id
    for dm in data['messages']:
        if dm.get('dm_id') == dm_id:
            all_dm_messages.append(dm)
        length = len(all_dm_messages)

    if length < start:
        raise InputError(description = 'Start is greater than the total messages')

    j = 0
    if length < 50: # if messages is less than 50
        while j < length: 
            message_dict = {}
            message_dict['message_id'] = all_dm_messages[j].get('dm_message_index')
            message_dict['u_id'] = all_dm_messages[j].get('sender')
            message_dict['message'] = all_dm_messages[j].get('message')
            message_dict['time_created'] = all_dm_messages[j].get('time_created')
            message_dict['reacts'] = all_dm_messages[j].get('reacts')
            message_dict['is_pinned'] = all_dm_messages[j].get('is_pinned')

            message_list.append(message_dict)
            j += 1
              
    else:    
        i = start
        while i < (start + 50): # for cases with greater than 50 messages
            message_dict = {}
            message_dict['message_id'] = all_dm_messages[i].get('message_index')
            message_dict['u_id'] = all_dm_messages[i].get('sender')
            message_dict['message'] = all_dm_messages[i].get('message')
            message_dict['time_created'] = all_dm_messages[i].get('time_created')
            message_dict['reacts'] = all_dm_messages[i].get('reacts')
            message_dict['is_pinned'] = all_dm_messages[i].get('is_pinned')
            
            message_list.append(message_dict)
            i += 1
            end = start + 50

    message_list.reverse()

    return {'messages' : message_list, 'start' : start, 'end' : end}
