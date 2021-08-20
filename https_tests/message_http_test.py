import pytest
import requests
import json
from http_tests.http_helpers import register_user, channels_create, create_dm
from http_tests.fixtures import clear_data, channel_set_up, message_chan_setup, dm_set_up
from src import config
from datetime import datetime
from datetime import timezone
import pytz
def test_message_send(clear_data, channel_set_up):
    '''
    Test that a message is successfully sent

    Parameters:
        token (str): token of the user calling the function
        channel_id (int) : the channel the message will be sent to
        message (str): the message

    Returns:
        Dictionary with the message id
    '''
    data = {
        'token' : channel_set_up[0]['token'], 
        'channel_id' : channel_set_up[3]['channel_id'], 
        'message' : 'lets do thissssss',
        }

    resp = requests.post(config.url + 'message/send/v2', json=data)
    load = resp.json()

    assert load['message_id'] == 1

def test_long_message(clear_data, channel_set_up):
    '''
    Test that input error is raised when message is more than 1000 characters

    Parameters:
        token (str): token of the user calling the function
        channel_id (int) : the channel the message will be sent to
        message (str): the message

    Returns:
        Raises input error
    '''  
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


    data = {
        'token' : channel_set_up[0]['token'], 
        'channel_id' : channel_set_up[3]['channel_id'], 
        'message' : message,
        }

    resp = requests.post(config.url + 'message/send/v2', json=data)

    assert resp.status_code == 400
    
def test_not_user_of_channel(clear_data, channel_set_up):
    '''
    Test that access error is raised when user is not part of channel

    Parameters:
        token (str): token of the user calling the function
        channel_id (int) : the channel the message will be sent to
        message (str): the message

    Returns:
        Raises access error
    '''

    # Generate a user that is not a part of the channel they want to send a message to
    user = register_user(config.url + 'auth/register/v2', 'shelbygoodkind@testemail.com', 'testpassworkdas12', 'shelby', 'goodkind')
    
    data = {
        'token' : user['token'], 
        'channel_id' : channel_set_up[3]['channel_id'], 
        'message' : 'hellooooooo',
        }

    resp = requests.post(config.url + 'message/send/v2', json=data)

    assert resp.status_code == 403

def test_message_edit(clear_data, message_chan_setup):
    '''
    Test that a message is successfully sent

    Parameters:
        token (str): token of the user calling the function
        channel_id (int) : the channel the message will be sent to
        message (str): the message

    Returns:
        Dictionary with the message id
    '''
    data = {
        'token' : message_chan_setup[0].get('token'), 
        'message_id' : message_chan_setup[4][1].get('message_id'), 
        'message' : 'we still goinggg',
        }

    resp = requests.put(config.url + 'message/edit/v2', json=data)

    assert resp.status_code == 200
    

def test_message_remove(clear_data, message_chan_setup):
    '''
    Test that a message is successfully sent

    Parameters:
        token (str): token of the user calling the function
        channel_id (int) : the channel the message will be sent to
        message (str): the message

    Returns:
        Dictionary with the message id
    '''
    data = {
        'token' : message_chan_setup[0].get('token'), 
        'message_id' : message_chan_setup[4][1].get('message_id'), 
        }

    resp = requests.delete(config.url + 'message/remove/v1', json=data)
    
    assert resp.status_code == 200

def test_message_share(clear_data, message_chan_setup):
    '''
    Test that a message is successfully sent

    Parameters:
        token (str): token of the user calling the function
        channel_id (int) : the channel the message will be sent to
        message (str): the message

    Returns:
        Dictionary with the message id
    '''
    share_data = {
        'token' : message_chan_setup[0].get('token'),
        'og_message_id' : message_chan_setup[4][1].get('message_id'),
        'message' : 'we still going',
        'channel_id': message_chan_setup[3].get('channel_id'),
        'dm_id' : -1,
    }
    resp = requests.post(config.url + 'message/share/v1', json=share_data)

    load = resp.json()

    assert load['shared_message_id'] == 1


def test_message_senddm(clear_data, dm_set_up):
    '''
    Test that a dm message is successfully sent

    Parameters:
        token (str): token of the user calling the function
        channel_id (int) : the channel the message will be sent to
        message (str): the message

    Returns:
        Dictionary with the message id
    '''
    message_data = {
        'token' : dm_set_up[0].get('token'), 
        'dm_id' : dm_set_up[3].get('dm_id'), 
        'message' : 'this is a test message',
        }

    resp = requests.post(config.url + 'message/senddm/v1', json=message_data)

    load = resp.json()

    assert load['message_id'] == 1

def test_message_dm_long(clear_data, dm_set_up):
    '''
    Test that a dm message is successfully sent

    Parameters:
        token (str): token of the user calling the function
        channel_id (int) : the channel the message will be sent to
        message (str): the message

    Returns:
        Dictionary with the message id
    '''
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
      

    message_data = {
        'token' : dm_set_up[0].get('token'), 
        'dm_id' : dm_set_up[3].get('dm_id'), 
        'message' : message,
        }

    resp = requests.post(config.url + 'message/senddm/v1', json=message_data)

    assert resp.status_code == 400

def test_not_dm_member(clear_data, dm_set_up):
    '''
    Test that access error is raised when user is not part of channel

    Parameters:
        token (str): token of the user calling the function
        channel_id (int) : the channel the message will be sent to
        message (str): the message

    Returns:
        Raises access error
    '''
    # Generate a user that does not belong to the dm
    user = register_user(config.url + 'auth/register/v2', 'jenniferjareau@testemail.com', 'testpassworkdas12', 'jennifer', 'jareau')
  
    data = {
        'token' : user.get('token'), 
        'dm_id' : dm_set_up[3].get('dm_id'), 
        'message' : 'hellooooooo',
        }

    resp = requests.post(config.url + 'message/senddm/v1', json=data)
    assert resp.status_code == 403

def test_notifications(clear_data, dm_set_up):
    # Invite the user and ensure 
    message_data = {
        'token' : dm_set_up[1].get('token'), 
        'dm_id' : dm_set_up[3].get('dm_id'), 
        'message' : '@jenniferjareau whats up',
        }
    resp = requests.post(config.url + 'message/senddm/v1', json=message_data)

    resp = requests.get(config.url + 'notifications/get/v1', params = {'token' : dm_set_up[0].get('token')})
    load = resp.json() 
    assert len(load) == 1
    
def test_react(clear_data, message_chan_setup):
    '''
    Test that function successfully reacts to a message
    '''
    data = {
        'token' : message_chan_setup[0].get('token'),
        'message_id' :message_chan_setup[4][0].get('message_id'),
        'react_id' : 1,
    }
    
    resp = requests.post(config.url + 'message/react/v1', json=data)
    
    assert resp.status_code == 200

def test_react_already_react(clear_data, message_chan_setup):
    '''
    Test that function raises input error when reacting to message that is already reacted 
    '''
    
    data = {
        'token' : message_chan_setup[0].get('token'),
        'message_id' : message_chan_setup[4][0].get('message_id'),
        'react_id' : 1,
    }
    
    resp = requests.post(config.url + 'message/react/v1', json=data)
    
    resp = requests.post(config.url + 'message/react/v1', json=data)
    
    assert resp.status_code == 400


def test_react_no_message(clear_data, message_chan_setup):
    '''
    Test that function raises input error when no message exists
    '''
    
    data = {
        'token' : message_chan_setup[0].get('token'),
        'message_id' : None,
        'react_id' : 1,
    }
    
    resp = requests.post(config.url + 'message/react/v1', json=data)
    
    assert resp.status_code == 400

def test_react_invalid_reactid(clear_data, message_chan_setup):
    '''
    #Test that function raises input error when react id is invalid 
    '''
    
    data = {
        'token' : message_chan_setup[0].get('token'),
        'message_id' : message_chan_setup[4][0].get('message_id'),
        'react_id' : 10,
    }
    
    resp = requests.post(config.url + 'message/react/v1', json=data)
    
    assert resp.status_code == 400

def test_unreact(clear_data, message_chan_setup):
    '''
    Test that function successfully unreacts to a message
    '''
    react_data = {
        'token' : message_chan_setup[0].get('token'),
        'message_id' :message_chan_setup[4][0].get('message_id'),
        'react_id' : 1,
    }
    
    requests.post(config.url + 'message/react/v1', json=react_data)

    data = {
        'token' : message_chan_setup[0].get('token'),
        'message_id' : message_chan_setup[4][0].get('message_id'),
        'react_id' : 1,
    }
    resp = requests.post(config.url + 'message/unreact/v1', json=data)
    
    assert resp.status_code == 200

def test_unreact_no_react(clear_data, message_chan_setup):
    '''
    Test that function raises input error when there is no reaction
    '''
    
    data = {
        'token' : message_chan_setup[0].get('token'),
        'message_id' : message_chan_setup[4][0].get('message_id'),
        'react_id' : 1,
    }
    
    resp = requests.post(config.url + 'message/unreact/v1', json=data)
    
    assert resp.status_code == 400


def test_unreact_no_message(clear_data, message_chan_setup):
    '''
    Test that function raises input error when no message exists
    '''
    
    data = {
        'token' : message_chan_setup[0].get('token'),
        'message_id' : None,
        'react_id' : 1,
    }
    
    resp = requests.post(config.url + 'message/unreact/v1', json=data)
    
    assert resp.status_code == 400

def test_unpin(clear_data, message_chan_setup):
    '''
    Test that function successfully unreacts to a message
    '''
    data = {
        'token' : message_chan_setup[0].get('token'),
        'message_id' :message_chan_setup[4][0].get('message_id'),
    }
    
    requests.post(config.url + 'message/pin/v1', json=data)

    resp = requests.post(config.url + 'message/unpin/v1', json=data)
    
    assert resp.status_code == 200

def test_unpin_already_pinned(clear_data, message_chan_setup):
    '''
    Test that function raises input error when a message has already been previously unpinned 
    '''
    
    data = {
        'token' : message_chan_setup[0].get('token'),
        'message_id' : message_chan_setup[4][0].get('message_id'),
    }
    requests.post(config.url + 'message/pin/v1', json=data)
    resp = requests.post(config.url + 'message/unpin/v1', json=data)
    assert resp.status_code == 200
    #call unpin again
    resp = requests.post(config.url + 'message/unpin/v1', json=data)

    assert resp.status_code == 400

def test_unpin_invalid_user(clear_data, message_chan_setup):
    '''
    Test that function raises input error when a user is invalid 
    '''
    valid_data = {
        'token' : message_chan_setup[0].get('token'),
        'message_id' : message_chan_setup[4][0].get('message_id'),
    }

    invalid_data = {
        'token' : 555,
        'message_id' : message_chan_setup[4][0].get('message_id'),
    }
    requests.post(config.url + 'message/pin/v1', json=valid_data)

    #call unpin 
    resp = requests.post(config.url + 'message/unpin/v1', json=invalid_data)

    assert resp.status_code == 403

def test_pin(clear_data, message_chan_setup):
    '''
    Test that function successfully pins a message
    '''
    data = {
        'token' : message_chan_setup[0].get('token'),
        'message_id' :message_chan_setup[4][0].get('message_id'),
    }
    
    resp = requests.post(config.url + 'message/pin/v1', json=data)
    
    assert resp.status_code == 200

def test_pin_already_pinned(clear_data, message_chan_setup):
    '''
    Test that function raises input error when a message has already been previously pinned 
    '''
    
    data = {
        'token' : message_chan_setup[0].get('token'),
        'message_id' : message_chan_setup[4][0].get('message_id'),
    }
    resp = requests.post(config.url + 'message/pin/v1', json=data)
    assert resp.status_code == 200
    #call pin again
    resp = requests.post(config.url + 'message/pin/v1', json=data)

    assert resp.status_code == 400

def test_pin_invalid_user(clear_data, message_chan_setup):
    '''
    Test that function raises input error when an invalid user attempts to call it 
    '''
    invalid_data = {
        'token' : 555,
        'message_id' : message_chan_setup[4][0].get('message_id'),
    }
    #call pin 
    resp = requests.post(config.url + 'message/pin/v1', json=invalid_data)

    assert resp.status_code == 403

def test_message_sendlater(clear_data, channel_set_up):
    '''
    Test that a message is successfully sent

    Parameters:
        token (str): token of the user calling the function
        channel_id (int) : the channel the message will be sent to
        message (str): the message

    Returns:
        Dictionary with the message id
    '''
    dt = datetime.now(pytz.timezone("GMT"))
    timestamp = dt.replace(tzinfo=timezone.utc).timestamp()

    data = {
        'token' : channel_set_up[0]['token'], 
        'channel_id' : channel_set_up[3]['channel_id'], 
        'message' : 'lets do thissssss',
        'time_sent':  timestamp + 5,
        }

    requests.post(config.url + 'message/sendlater/v1', json=data)


    data = {
    'token' : channel_set_up[0]['token'], 
    'channel_id' : channel_set_up[3]['channel_id'], 
    'message' : 'hehehehe',
    'time_sent':  timestamp + 5,
    }
    resp = requests.post(config.url + 'message/sendlater/v1', json=data)


    assert resp.status_code == 200

def test_message_sendlaterdm(clear_data, dm_set_up):

    dt = datetime.now(pytz.timezone("GMT"))
    timestamp = dt.replace(tzinfo=timezone.utc).timestamp()

    data = {
        'token' : dm_set_up[0].get('token'),
        'dm_id' : dm_set_up[3].get('dm_id'),
        'message' : 'i like turtles',
        'time_sent' : timestamp + 5,
    }

    requests.post(config.url + 'message/sendlaterdm/v1', json=data)

    
    data = {
        'token' : dm_set_up[0]['token'],
        'dm_id' : dm_set_up[3].get('dm_id'),
        'message' : 'i do not like turtles',
        'time_sent' : timestamp + 5,
    }

    resp = requests.post(config.url + 'message/sendlaterdm/v1', json=data)


    assert resp.status_code == 200