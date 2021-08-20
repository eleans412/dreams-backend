from src.error import AccessError, InputError
from src.data import data
from src.channel import channel_invite_v2, channel_join_v2, channel_messages_v2
from src.auth import auth_login_v2, auth_register_v2
from src.channels import channels_create_v2
from src.message import message_send_v2
from src.other import clear_v1
from src.helper import check_valid_info
import pytest
from tests.fixture import channel_set_up, auth_set_up

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

def test_channel_messages(channel_set_up):
    #Test functionality of channel_messages

    string = 'hello there world'
    message_list = string.split()
    
    # Loop through message_list for message_send to send messages
    for message in message_list:
        message_send_v2(channel_set_up[0].get('token'), channel_set_up[2].get('channel_id'), message)

    message_test = channel_messages_v2(channel_set_up[0].get('token'),channel_set_up[2].get('channel_id'), 0)

    # Assert the first and last string message to confirm order
    assert message_test['messages'][0]['message'] == 'world'
    assert message_test['messages'][2]['message'] == 'hello'

    # Assert the length of messages is correct
    assert len(message_test['messages']) == 3

    # Assert that start and end are correct
    assert message_test['start'] == 0
    assert message_test['end'] == -1

def test_bad_channel_input(auth_set_up):
    #Test that an input error when invalid input for channel is passed in

    with pytest.raises(InputError):
        channel_messages_v2(auth_set_up[0].get('token'), None, 0)

def test_many_messages(channel_set_up):

    #Test that function can cope with more than 50 messages,
    #check returning the message itself, as well as start and end ints

    extra_long_string = 'Busy old fool, unruly Sun, Why dost thou thus, Through windows, and through curtains, call on us? \
        Must to thy motions lovers seasons run? Saucy pedantic wretch, go chide Late school-boys and sour prentices, \
        Go tell court-huntsmen that the king will ride, Call country ants to harvest offices; Love, all alike, no season knows nor clime, \
        Nor hours, days, months, which are the rags of time. Thy beams so reverend, and strong Why shouldst thou think? \
        I could eclipse and cloud them with a wink, But that I would not lose her sight so long. If her eyes have not blinded thine, \
        Look, and to-morrow late tell me, Whether both th Indias of spice and mine Be where thou leftst them, or lie here with me. \
        Ask for those kings whom thou sawst yesterday, And thou shalt hear, "All here in one bed lay. Shes all states, and all princes I; \
    	Nothing else is; Princes do but play us; compared to this, All honours mimic, all wealth alchemy. Thou, Sun, art half as happy as we, \
    	In that the worlds contracted thus; Thine age asks ease, and since thy duties be To warm the world, thats done in warming us. \
        Shine here to us, and thou art everywhere; This bed thy center is, these walls thy sphere.'

    # Split the long string into messages
    # Store these messages into a message_list to loop through message_send
    message_list = extra_long_string.split()
    
    # Loop through message_list for message_send to send more than 50 messages
    for message in message_list:
        message_send_v2(channel_set_up[0].get('token'), channel_set_up[2].get('channel_id'), message)

    
    # Call channel_messages
    messages_returned = channel_messages_v2(channel_set_up[0].get('token'), channel_set_up[2].get('channel_id'), 70)

    # Assert the first and last string to confirm the order messages are returned in
    # Get the first and last index to check
    print(messages_returned)
    assert messages_returned['messages'][0]['message']  == 'leftst'
    assert messages_returned['messages'][49]['message'] == 'and'

    # Assert the length of messages returned is correct
    assert len(messages_returned['messages']) == 50

    # Assert that start and end are correct
    assert messages_returned['start'] == 70
    assert messages_returned['end'] == 120

def test_start_error(channel_set_up):
    #Test InputError is raised if start index is greater than the total number of messages

    string = 'hello there world'
    message_list = string.split()
    
    # Loop through message_list for message_send to send messages
    for message in message_list:
        message_send_v2(channel_set_up[0].get('token'), channel_set_up[2].get('channel_id'), message)

    with pytest.raises(InputError):
        channel_messages_v2(channel_set_up[0].get('token'), channel_set_up[2].get('channel_id'), 90)

def test_bad_channel_id(channel_set_up):
    #Test InputError is raised when channel id does not exist

    bad_channel_id = {'channel_id' : 132}
    
    with pytest.raises(InputError):
        channel_messages_v2(channel_set_up[0].get('token'), bad_channel_id['channel_id'], 2)

def test_bad_user_id(channel_set_up):
    #Test InputError is raised when user_id does not exist
    
    with pytest.raises(AccessError):
        channel_messages_v2(None, channel_set_up[2].get('channel_id'), 2)

def test_not_member(channel_set_up):
    #Test AccessError is raised when a member is not a part of the channel

    auth_user_id3 = auth_register_v2('stantheman@testemail.com', 'passqoed31', 'stan', 'roberts')
    with pytest.raises(AccessError):
        channel_messages_v2(auth_user_id3['token'], channel_set_up[2]['channel_id'], 2)

def test_many_users_message():
    #Test that the message outputted is correct for messages sent by different users

    clear_v1()
    # Set up and register users and channels
    user1 = auth_register_v2('rebeccagild@testemail.com', 'pass41242', 'rebecca', 'gilroy')
    user2 = auth_register_v2('stantheman@testemail.com', 'passqoed31', 'stan', 'roberts')
    user3 = auth_register_v2('tonishalifoe@testemail.com', 'pOsWord36', 'toni', 'shalifoe')
    user4 = auth_register_v2('shelbymanning@testemail.com', 'poasswoprpd12', 'shelby', 'manning')
    
    test_channel = channels_create_v2(user1['token'], 'new_channel', True)
    channel_invite_v2(user1['token'], test_channel['channel_id'], user2['auth_user_id'])
    channel_join_v2(user2['token'], test_channel['channel_id'])

    channel_invite_v2(user1['token'], test_channel['channel_id'], user3['auth_user_id'])
    channel_join_v2(user3['token'], test_channel['channel_id'])

    channel_invite_v2(user1['token'], test_channel['channel_id'], user4['auth_user_id'])
    channel_join_v2(user4['token'], test_channel['channel_id'])

    string = 'test this thing works'
    message_list = string.split()
    
    # Loop through message_list for message_send to send messages
    
    message_send_v2(user1['token'], test_channel['channel_id'], message_list[0])
    message_send_v2(user2['token'], test_channel['channel_id'], message_list[1])
    message_send_v2(user3['token'], test_channel['channel_id'], message_list[2])
    message_send_v2(user4['token'], test_channel['channel_id'], message_list[3])

    # Call Channel messages
    message_check = channel_messages_v2(user1['token'], test_channel['channel_id'], 0)

    # Assert the first and last string message to confirm order
    assert message_check['messages'][0].get('message') == 'works'
    assert message_check['messages'][3].get('message') == 'test'

    # Assert the length of messages is correct
    assert len(message_check['messages']) == 4

    # Assert that start and end are correct
    assert message_check['start'] == 0
    assert message_check['end'] == -1

def test_message_to_different_chan():
    #Test that the message is printed from the requested channel only

    clear_v1()

    user1 = auth_register_v2('rebeccagild@testemail.com', 'pass41242', 'rebecca', 'gilroy')
    user2 = auth_register_v2('stantheman@testemail.com', 'passqoed31', 'stan', 'roberts')
    user3 = auth_register_v2('tonishalifoe@testemail.com', 'pOsWord36', 'toni', 'shalifoe')
    user4 = auth_register_v2('shelbymanning@testemail.com', 'poasswoprpd12', 'shelby', 'manning')

    test_channel = channels_create_v2(user1['token'], 'new_channel', True)
    test_channel2 = channels_create_v2(user1['token'], 'second_channel', True)

    channel_invite_v2(user1['token'], test_channel2['channel_id'], user2['auth_user_id'])
    channel_join_v2(user2['token'], test_channel2['channel_id'])

    channel_invite_v2(user1['token'], test_channel['channel_id'], user3['auth_user_id'])
    channel_join_v2(user3['token'], test_channel['channel_id'])

    channel_invite_v2(user1['token'], test_channel2['channel_id'], user4['auth_user_id'])
    channel_join_v2(user4['token'], test_channel2['channel_id'])

    message_send_v2(user1['token'], test_channel['channel_id'], 'test')
    message_send_v2(user2['token'], test_channel2['channel_id'], 'this')
    message_send_v2(user3['token'], test_channel['channel_id'], 'function')
    message_send_v2(user4['token'], test_channel2['channel_id'], 'works')

    channel_check = channel_messages_v2(user2['token'], test_channel2['channel_id'], 0)

    # Assert the first and last string message to confirm order
    assert channel_check['messages'][0].get('message') == 'works'
    assert channel_check['messages'][1].get('message') == 'this'

    # Assert the length of messages is correct
    assert len(channel_check['messages']) == 2

    # Assert that start and end are correct
    assert channel_check['start'] == 0
    assert channel_check['end'] == -1

def test_no_messages(channel_set_up):
    channel_check = channel_messages_v2(channel_set_up[0]['token'], channel_set_up[2]['channel_id'], 0)
    assert channel_check['start'] == 0
    assert channel_check['end'] == -1
    assert len(channel_check['messages']) == 0