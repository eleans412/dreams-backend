from src.data import getData
from src.error import InputError, AccessError
from src.helper import check_valid_info, find_user_id, get_user_info, check_valid, user_message_count, is_jpg, get_timestamp
from src.helper import all_dm_count, all_message_count, get_involvement_rate
from src.channels import channels_list_v2, channels_listall_v2
from src.dm import dm_list_v1
import urllib.request
from PIL import Image
from src import config
import os 
import requests



def user_profile_v2(token, u_id):
    """
    For a valid user, returns information about their user_id, email, first name, last name, and handle

    Arguments:
        token (str) - the user's token
        u_id (int) - the user's u_id
    
    Exceptions:
        InputError - User with u_id is not a valid user
    
    Return Value:
        user (dict) - Dictionary containing: 
            - u_id (int)
            - email (string)
            - name_first (string)
            - name_last (string)
            - handle_str (string)
            - profile_img_url (string)
    """
    data = getData()
    # Ensure that u_id is an int
    u_id = int(u_id)
    auth_user_id = find_user_id(token)
    if auth_user_id == False:
        raise AccessError(description = 'User is not a registered user')

    if check_valid_info(data['users'], auth_user_id) and check_valid_info(data['users'], u_id):
            user_info = {
                'u_id' : data['users'][u_id - 1].get('auth_user_id'),
                'email' : data['users'][u_id - 1].get('email'),
                'name_first' : data['users'][u_id - 1].get('f_name'),
                'name_last' : data['users'][u_id - 1].get('l_name'),
                'handle_str' : data['users'][u_id - 1].get('handle_str'),
                'profile_img_url': data['users'][u_id - 1].get('profile_img_url'),
            }
    else:
        raise InputError(description ="Provided u_id does not belong to a valid user")
    return {'user' : user_info}

def user_profile_setname_v2(token, name_first, name_last):
    """
    Update the authorised user's first and last name

    Arguments:
        token (str) - the user's token
        name_first (str) - the user's updated first name
        name_last (str) - the user's updated last name
    
    Exceptions:
        InputError - name_first is not between 1 and 50 characters inclusively in length
        InputError - name_last is not between 1 and 50 characters inclusively in length
    
    Return Value:
        None
    """
    #takes in token, new first and last name
    data = getData()
    #checks that inputs for requested first name and last name are valid 
    if not 0 < len(name_first) <= 50 or not 0 < len(name_last) <= 50: 
        raise InputError("First name or last name is not between 1 and 50 characters inclusively in length") 
    
    auth_user_id = find_user_id(token)
    if check_valid_info(data['users'], auth_user_id):
        #if token is found, set new names as requested
        data['users'][auth_user_id - 1]['f_name'] = name_first
        data['users'][auth_user_id - 1]['l_name'] = name_last
        return {
        }
    else:  
        raise AccessError(description = "Can only set names for a registered user")                     

def user_profile_setemail_v2(token, email):
    """
    Update the authorised user's email address

    Arguments:
        token (str) - the user's token
        email (str) - the user's email
    
    Exceptions:
        InputError - Email entered is not a valid email using the method provided
        InputError - Email address is already being used by another user
    
    Return Value:
        None
    """
    data = getData()
    #check new email format is valid
    if not check_valid(email):
        raise InputError(description ="Requested new email is not valid")

    # Check that the email being changed to is not already being used by another user
    for user in data['users']:
        if user.get('email') == email:
            raise InputError(description ='Email already being used by another user')

    auth_user_id = find_user_id(token)
    if check_valid_info(data['users'], auth_user_id):
        #if token is found, set new names as requested
        data['users'][auth_user_id - 1]['email'] = email
        
    else:  
        raise AccessError(description = "Can only set email for a registered user")
    
    return {}

def user_profile_sethandle_v1(token, handle_str):
    """
    Update the authorised user's handle (i.e. display name)

    Arguments:
        token (str) - the user's token
        handle_str (str) - the user's handle
    
    Exceptions:
        InputError - handle_str is not between 3 and 20 characters inclusive
        InputError - handle is already used by another user
    
    Return Value:
        None
    """
    data = getData()
    #check if handlestr is valid length, ie 3 <= handlestring <= 20
    if len(handle_str)-1 <= 3 or len(handle_str)-1 >= 20: 
        raise InputError(description ="Requested handle is not of valid length")

    #check that handle is not already in use 
    i = 0
    while i < len(data["users"]):
        if data["users"][i].get("handle_str") == handle_str:
            raise InputError(description = "This handle is already in use by another user")
        i += 1

    auth_user_id = find_user_id(token)
    if check_valid_info(data['users'], auth_user_id):
        #if token is found, set new names as requested
        data['users'][auth_user_id - 1]['handle_str'] = handle_str
        return {
        }
    else:  
        raise AccessError(description = "Can only set handle for a registered user")

def user_stats_v1(token):
    """
    Fetches the required statistics about this user's use of UNSW Dreams
        
    Arguments:
        token (str) - the user's token
    
    Exceptions:
        N/A

    Return Value:
        user_stats (dict) - Dictionary of shape: 
            - channels_joined (int)
            - dms_joined (int)
            - messages_sent (int)
            - involvement_rate (float)
    """
    data = getData()
    empty_stats = False

    # Get the current timestamp
    time_stamp = get_timestamp()

    #set desired stats to zero
    num_channels_joined = 0
    num_dms_joined = 0
    num_msgs_sent = 0
    num_dreams_channels = 0
    num_dreams_dms = 0
    num_dreams_msgs = 0
    
    auth_user_id = find_user_id(token)
    if auth_user_id == False: 
        raise AccessError(description ="This is not a valid user")
    
    #find total number of dreams channels
    all_channels_list = channels_listall_v2(token)
    num_dreams_channels = len(all_channels_list)

    #find total number of dreams dms
    num_dreams_dms = all_dm_count()

    #find total number of dreams messages
    num_dreams_msgs = all_message_count()

    #find num of channels joined
    channel_list = channels_list_v2(token)
    num_channels_joined = len(channel_list["channels"])

    #find num of dm's joined
    dm_list = dm_list_v1(token)
    num_dms_joined = len(dm_list['dms'])
    
    #find num of messages sent
    num_msgs_sent = user_message_count(token)

    #calculate involvment rate
    involvement_rate = get_involvement_rate(num_channels_joined, num_dms_joined, num_msgs_sent, num_dreams_channels, num_dreams_dms, num_dreams_msgs)


    # Check if there are preexisting stats, if not generate user stats
    if data['users'][auth_user_id - 1].get('user_stats') == None:
        user_stats = {
            'channels_joined' : [{'num_channels_joined' : num_channels_joined, 'time_stamp': time_stamp}],
            'dms_joined' : [{'num_dms_joined' : num_dms_joined, 'time_stamp' : time_stamp}], 
            'messages_sent' : [{'num_messages_sent' : num_msgs_sent, 'time_stamp' : time_stamp}], 
            'involvement_rate' : round(involvement_rate, 1), 
        }
        data['users'][auth_user_id - 1]['user_stats'] = user_stats
        empty_stats = True

    # Update the user stat if user stats for the profile if users stats key already exists
    if not empty_stats:
        # Update channel joined key
        if num_channels_joined > data['users'][auth_user_id - 1]['user_stats']['channels_joined'][-1]['num_channels_joined']:
            channel_dict = {'num_channels_joined' : num_channels_joined, 'time_stamp': time_stamp}
            data['users'][auth_user_id - 1]['user_stats']['channels_joined'].append(channel_dict)
        # Update dm joined key
        if num_dms_joined > data['users'][auth_user_id - 1]['user_stats']['dms_joined'][-1]['num_dms_joined']:
            dm_dict = {'num_dms_joined' : num_dms_joined, 'time_stamp' : time_stamp}
            data['users'][auth_user_id - 1]['user_stats']['dms_joined'].append(dm_dict)
        # Update message send key    
        if num_msgs_sent > data['users'][auth_user_id - 1]['user_stats']['messages_sent'][-1]['num_messages_sent']:
            msg_dict = {'num_messages_sent' : num_msgs_sent, 'time_stamp' : time_stamp}
            data['users'][auth_user_id - 1]['user_stats']['messages_sent'].append(msg_dict)
        
        #calculate involvment rate to update the rate for additional channels and dms
        involvement_rate = get_involvement_rate(num_channels_joined, num_dms_joined, num_msgs_sent, num_dreams_channels, num_dreams_dms, num_dreams_msgs)
        data['users'][auth_user_id - 1]['user_stats']['involvement_rate'] = round(involvement_rate, 1)
    return {'user_stats' : data['users'][auth_user_id - 1]['user_stats']}

def user_profile_uploadphoto_v1(token, img_url, x_start, y_start, x_end, y_end): 
    """
    Given a URL of an image on the internet, crops the image within bounds (x_start, y_start) and (x_end, y_end). Position (0,0) is the top left.

    Arguments: 
    token (str) - unique session id for the authorised user 
    img_url (str) - url of the image to be uploaded 
    x_start (int) - x coordinate for the start of the crop 
    y_start (int) - y coordinate for the end of the crop 
    x_end (int) - x coordinate for the end of the crop 
    y_end (int) - y coordinate for the end of the crop 
    
    Exceptions:
        InputError - img_url returns an HTTP status other than 200.
        InputError - any of x_start, y_start, x_end, y_end are not within the dimensions of the image at the URL.
        InputError - Image uploaded is not a JPG
    
    Return Value: 
        None
    """
    data = getData()
    
    #if the response status is not 200, raise an input error
    status = requests.get(img_url)
    if status.status_code != 200:
        raise InputError(description="This image url is not valid")

    #get the size of the image from url 
    image = Image. open(urllib. request. urlopen(img_url))
    width, height = image. size

    #check negative coordinates for crop 
    if x_start < 0 or y_start < 0 or x_end < 0 or y_start < 0: 
        raise InputError(description="Invalid bounds for crop - negative values are invalid")

    #check if end crop values are below start values
    if x_end < x_start or y_end < y_start:
        raise InputError(description="Invalid bounds for crop - start crop co-ords are invalid")

    #check if end crop values are more than the image size 
    if x_end > width or y_end > height:
        raise InputError(description="Invalid bounds for crop - end crop co-ords are invalid")
   
    #if the image is not a jpg, raise an input error
    if not is_jpg(img_url): 
        raise InputError(description="This image is not a jpg")
    
    auth_user_id = find_user_id(token)
    if auth_user_id == False: 
        raise AccessError(description ="This is not a valid user")

    #retrieve image and save 
    imagename = str(auth_user_id) + "_profile.jpg"
    urllib.request.urlretrieve(img_url, imagename)
    # opens the image 
    imageObject = Image.open(imagename)
    #crop the image 
    cropped = imageObject.crop((x_start, y_start, x_end, y_end))
    
    #save the image, first must check if the static file exists to save the cropped image. If not, create one 
    path = "static"
    if not os.path.exists(path): 
        os.mkdir(path)

    cropped.save("static/" + imagename)
    
    profile_image_url = str(config.url) + "static/" + imagename
    #store the image url 

    data['users'][auth_user_id - 1]['profile_img_url'] = profile_image_url

    return { 
    }
