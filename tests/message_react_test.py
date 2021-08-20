from src.other import clear_v1, search_v2
from src.channel import channel_join_v2, channel_invite_v2
from src.channels import channels_create_v2
from src.auth import auth_login_v2, auth_register_v2
from src.dm import dm_create_v1, dm_invite_v1
from src.message import message_send_v2, message_senddm_v1, message_share_v1, notifications_get_v1, message_react_v1
from src.error import AccessError, InputError
import pytest
from tests.fixture import channel_set_up, dm_set_up
from src.data import getData
from src.helper import get_end_nums, check_valid, check_existing, store


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

def test_functionality_dm(dm_set_up):
    #tests functionality on dm messages
    data = getData()
  
    user = auth_register_v2('validemail4@gmail.com', '123abc!@#', 'Ali', 'Khan')
    
    dm_invite_v1(dm_set_up[0]['token'], dm_set_up[2]['dm_id'], user['auth_user_id'])
    #user messages dm
    message_id1 = message_senddm_v1(user['token'], dm_set_up[2]["dm_id"], "React with thumbs up if you have done this weeks labs")
    
    #user 2 and user 3 react to message
    message_react_v1(dm_set_up[1]["token"], message_id1["message_id"], 1)
    message_react_v1(user["token"], message_id1["message_id"], 1)
    
    assert_check = False
    if 2 in data["messages"][1- 1]["reacts"][1 - 1]["u_ids"] and 3 in data["messages"][1 - 1]["reacts"][1 - 1]["u_ids"]:
        assert_check = True
    
    assert assert_check == True
   


def test_functionality_channel(channel_set_up):
    
    #tests functionality on channel messages

    data = getData()

    # Create a new user, invite them to the channel to react
    user = auth_register_v2('validemail4@gmail.com', '123abc!@#', 'Ali', 'Khan')
   
    channel_invite_v2(channel_set_up[0]["token"], channel_set_up[2]["channel_id"], user["auth_user_id"]) 
    channel_join_v2(user["token"], channel_set_up[2]["channel_id"])

    message_id1 = message_send_v2(channel_set_up[0]["token"], channel_set_up[2]["channel_id"], "React with thumbs ")
    
    #user 2 and user 3 react ot message
    message_react_v1(channel_set_up[1]["token"], message_id1["message_id"], 1)
    message_react_v1(user["token"], message_id1["message_id"], 1)
    
    assert_check = False
    if 2 in data["messages"][1- 1]["reacts"][1 - 1]["u_ids"] and 3 in data["messages"][1 - 1]["reacts"][1 - 1]["u_ids"]:
        assert_check = True
    
    assert assert_check == True

  
#Input errors: 
def test_message_invalid(dm_set_up):
    #message_id is not a valid message within a channel or DM that the authorised user has joined
    
    message_id1 = message_senddm_v1(dm_set_up[0]['token'], dm_set_up[2]["dm_id"], "React with thumbs up") 
    message_react_v1(dm_set_up[1]["token"], message_id1["message_id"], 1)
    message_id2 = {"message_id" : 2}
       
    with pytest.raises(InputError):
        message_react_v1(dm_set_up[1]["token"], message_id2["message_id"], 1)


def test_invalid_reactid(dm_set_up):
    
    message_id1 = message_senddm_v1(dm_set_up[1]['token'], dm_set_up[2]["dm_id"], "React with thumbs up") 
       
    with pytest.raises(InputError):
        message_react_v1(dm_set_up[1]["token"], message_id1["message_id"], 10)
    

def test_already_reacted(dm_set_up):

    
    message_id1 = message_senddm_v1(dm_set_up[1]['token'], dm_set_up[2]["dm_id"], "React with thumbs up") 
    message_react_v1(dm_set_up[0]["token"], message_id1["message_id"], 1)    
    
    with pytest.raises(InputError):
        message_react_v1(dm_set_up[0]["token"], message_id1["message_id"], 1) 
   

#Access errors:

def test_invalid_member_dm(dm_set_up):
    #The authorised user is not a member of the channel or DM that the message is within
    
    user = auth_register_v2('validemail5@gmail.com', '123abc!@#', 'Daisy', 'Wu')
    
    message_id1 = message_senddm_v1(dm_set_up[1]['token'], dm_set_up[2]["dm_id"], "React with thumbs up")  
    
    with pytest.raises(AccessError):
        message_react_v1(user["token"], message_id1["message_id"], 1) 

