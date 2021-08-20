from src.other import clear_v1
from src.channel import channel_join_v2, channel_invite_v2
from src.channels import channels_create_v2
from src.auth import auth_register_v2
from src.message import message_send_v2
from tests.fixture import channel_set_up
from src.error import AccessError, InputError
from src.admin import admin_userpermissions_change_v1
from src.data import data
from tests.fixture import auth_set_up, channel_set_up, message_set_up
import pytest

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

def test_functionality(channel_set_up):
    #Test that a message is successfully sent to a channel

    message_id = message_send_v2(channel_set_up[0]['token'], channel_set_up[2]['channel_id'], 'hello')

    # Check the message ID has been added to the channel's message key value
    assert message_id == {'message_id' : 1}

def test_many_chars(channel_set_up):
    #Test that an InputError is raised when message is more than 1000 characters

    # Generate string to send as message
    message = 'Water. Earth. Fire. Air. My grandmother used to tell me stories about the old days, a time \
    of peace when the Avatar kept balance between the Water Tribes, Earth Kingdom, Fire Nation, and Air Nomads. \
    But that all changed when the Fire Nation attacked. Only the Avatar mastered all four elements. Only he could \
    stop the ruthless firebenders. But when the world needed him most, he vanished. A hundred years have passed \
    and the Fire Nation is nearing victory in the War. Two years ago, my father and the men of my tribe journeyed \
    to the Earth Kingdom to help fight against the Fire Nation, leaving me and my brother to look after our tribe. \
    Some people believe that the Avatar was never reborn into the Air Nomads, and that the cycle is broken. But I \
    havent lost hope. I still believe that somehow, the Avatar will return to save the world. \
    "Earth. Fire. Air. Water. When I was a boy, my father, Avatar Aang, told me the story of how he and his friends \
    heroically ended the Hundred Year War. Avatar Aang and Fire Lord Zuko transformed the Fire Nation colonies into the \
    United Republic of Nations, a society where benders and nonbenders from all over the world could live and thrive together\
    in peace and harmony. They named the capital of this great land Republic City. Avatar Aang accomplished many remarkable\
    things in his life, but sadly, his time in this world came to an end. And like the cycle of the seasons, the cycle \
    of the Avatar began anew.'

    with pytest.raises(InputError):
        message_send_v2(channel_set_up[0]['token'], channel_set_up[2]['channel_id'], message)

def test_user_not_member(channel_set_up):
    #Test that an AccessError is raised when the user is not a member of the channel

    #register an additional user, who is not part of the channel set up in channel_set_up fixture
    auth_user_id3 = auth_register_v2('validemail03@gmail.com', '123abc!@#', 'Bennett', 'Frerck')
        
    # User not a part of channel tries to send message to channel they don't belong to
    with pytest.raises(AccessError):
        message_send_v2(auth_user_id3['token'], channel_set_up[2]['channel_id'], 'hello there')

def test_channel_bad(channel_set_up):
    #Test that an AccessError is raised when trying to send a message to an invalid channel
    
    bad_channel_id = {'channel_id' : 456132}
    
    with pytest.raises(InputError):
        message_send_v2(channel_set_up[0]['token'], bad_channel_id['channel_id'], 'hello there')

def test_dream_owner_message(channel_set_up):
    #Test that a dream owner is able to send messages to any channel

    # Set up a new user to become a dream owner to send a message to
    new_user = auth_register_v2('annabethchase@testemail.com', 'password123523', 'annabeth', 'chase')
    admin_userpermissions_change_v1(channel_set_up[0].get('token'), new_user.get('auth_user_id'), 1)

    # **Dreams** owner sends message to the channel
    message1 = message_send_v2(new_user['token'], channel_set_up[2]['channel_id'], 'hello')

    # Check the message has been successfully sent
    assert data['messages'][0]['message'] == 'hello'
    assert message1 == {'message_id' : 1}

def test_message_diff_channels():
    #Test that messages sent to different channels do not share the same ID

    # Clear any preset data
    clear_v1()

    user1 = auth_register_v2('taylorhickson@testemail.com','password11', 'taylor', 'hickson')

    channel_id1 = channels_create_v2(user1['token'], 'motherland', True)
    channel_id2 = channels_create_v2(user1['token'], 'fort salem', True)
    channel_id3 = channels_create_v2(user1['token'], 'cession', True)
    
    message_id1 = message_send_v2(user1['token'], channel_id1['channel_id'], 'hello')
    message_id2 = message_send_v2(user1['token'], channel_id2['channel_id'], 'there')
    message_id3 = message_send_v2(user1['token'], channel_id3['channel_id'], 'world')


    # Check the message has been added to the message dictionary 
    # Check the message ID has been added to the channel's message key value
    assert message_id1 == {'message_id' : 1}
    assert message_id2 == {'message_id' : 2}
    assert message_id3 == {'message_id' : 3}

    for message in data['messages']:
        check_message1 = message.get('channel_message_index')
        check_message2 = message.get('channel_message_index')
        check_message3 = message.get('channel_message_index')

    assert check_message1 == 0
    assert check_message2 == 0
    assert check_message3 == 0

def test_wrong_input(channel_set_up):
    #test for accesserror when invalid user tries to send message

    with pytest.raises(AccessError):
        message_send_v2(123, channel_set_up[2].get('channel_id'), 'hi')