from src.data import getData
from src.error import AccessError, InputError
from src.helper import check_valid_info, check_members, add_to_channel_member_list,  join_channel, find_user_id

def admin_user_remove_v1(token, u_id):
    """
    Given a User by their user ID, remove the user from the Dreams.
    Dreams owners can remove other **Dreams** owners (including the original first owner).
    Once users are removed from **Dreams**, the contents of the messages they sent will be replaced by 'Removed user'.
    Their profile must still be retrievable with user/profile/v2, with their name replaced by 'Removed user'. 
    
    Arguments:
        token (str) - the user's token that is requesting user remove
        u_id (int) - the user's u_id that is being removed
    
    Exceptions:
        InputError - u_id does not refer to a valid user
        InputError - The user is currently the only owner
        AccessError - The authorised user is not an owner
    
    Return Value:
        None
    """
    data = getData()
    channels_in = True
    dms_in = True
    # Find the auth_user_id requesting the permission change
    auth_user_id = find_user_id(token)

    auth_owner_valid = False

    #check that auth_user_id and channel_id exist
    uid_valid = check_valid_info(data['users'], u_id)
    auth_user_id_valid = check_valid_info(data['users'], auth_user_id)
    if not auth_user_id_valid:
        raise AccessError(description = 'Invalid token')

    #if user_id or channel_id is invalid
    if uid_valid == False:
        raise InputError("User and/or uid does not exist")

    #check that auth_user_id is an owner
    for users in data['users']:
        if users.get('auth_user_id') is auth_user_id:
            if users.get('global_permissions') == 1:
                auth_owner_valid = True

    #input error is there is only one owner
    count = 0
    for users in data['users']:
        if users.get('global_permissions') == 1:
            count += 1
    if count == 1 and u_id == auth_user_id:
        raise InputError(description ="Cannot remove owner. There is only one owner")

    #access error if u_id is not an owner
    if auth_owner_valid == False:
        raise AccessError(description = "auth_user_id is not an owner")

    #remove user
    for users in data['users']:
        if users.get('auth_user_id') == u_id:
            users['name_first'] = 'Removed '
            users['name_last'] = 'User'
            users['email'] = ''
            users['handle_str'] = ''
            users['profile_img_str'] = ''
    #"replace the messages as 'removed owner'"
    if data.get('messages'):
        for message in data['messages']:
            if message.get('sender') == u_id:
                message['message'] = "Removed User"

    # Check if the user is in dm and channel

    if data['users'][u_id -1].get('channels_in') == None:
        channels_in = False

    if data['users'][u_id - 1].get('dms_in') == None:
        dms_in = False
    if channels_in:
        for channel in data['channels']:
            for owner in channel.get('owner_members'):
                if owner.get('u_id') == u_id:
                    channel['owner_members'].remove(owner)
            for member in channel.get('all_members'):
                if member.get('u_id') == u_id:
                    channel['all_members'].remove(member)

    if dms_in:
        for dm in data['dms']:
            for member in dm.get('all_members'):
                if member.get('u_id')== u_id:
                    dm['all_members'].remove(member)

    return {} 

def admin_userpermissions_change_v1(token, u_id, permission_id):
    """
    Given a user by their u_id, change their permissions to the one input by permission_id

    Arguments:
        token (str) - the user's token that is requesting permission change
        u_id (int) - the user's u_id that is having their permission changed
        permission_id (int) - the user's permission as a member or owner
    
    Exceptions:
        InputError - u_id does not refer to a valid user
        InputError - permission_id does not refer to a value permission
        AccessError - The authorised user is not an owner

    Return Value:
        None
    """
    data = getData()

    auth_valid = False
    user_valid = False
    dream_user = False
    owner_count = 0
    # Find the auth_user_id requesting the permission change
    auth_user_id = find_user_id(token)

    # Confirm that the token and u_id are valid users
    # Raise input error if they are not valid users
    auth_valid = check_valid_info(data['users'], auth_user_id)
    user_valid = check_valid_info(data['users'], u_id)

    if not auth_valid or not user_valid:
        raise InputError(description ='Token or user invalid. Cannot change permissions')

    # Check what permissions are being requested to be changed
    # Check that the token has the permissions required to change the permissions
    # Check if the user is a **Dreams** Owner
    # Count how many **Dreams** Owners there are
    for users in data['users']:
        if users.get('auth_user_id') is auth_user_id:
            if users.get('global_permissions') == 1:
                dream_user = True
                owner_count += 1

    # If 1 and 2 - global permissions 
    # Check that there is at least 1 dream owner if the owner wants to change to be just a member
    if not dream_user:
        raise AccessError(description = 'User does not have permissions to request this change')
    
    if not permission_id == 1 and not permission_id == 2:
        # If the permission id is none of the above, raise an InputError 
        raise InputError(description = 'Permission id is not valid, cannot change permission')
    
    for user in data['users']:
        # Find the user we want to change permission for and change their global permissions
        if user.get('auth_user_id') is u_id:
            if owner_count == 1 and u_id is auth_user_id:
                raise InputError(description = 'Cannot change permissions, there is only one global owner')
            #print(user.get('global_permissions'))
            #print(permission_id)
            if user.get('global_permissions') is permission_id:
                raise InputError(description = 'Permission Id already set, unable to change')
            user['global_permissions'] = permission_id
        
    return {
    }
s