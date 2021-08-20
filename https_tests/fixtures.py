import pytest
import requests
from src import config
from http_tests.http_helpers import register_user, channels_create, channel_invite, channel_join, create_dm, message_send, dm_message_send, add_owner

@pytest.fixture
def clear_data():
    '''
    Fixture will clear preexisting data
    '''
    response = requests.delete(config.url + 'clear/v1')
    return response.json()

@pytest.fixture
def user_reg():
    '''
    Fixture will register 1 user
    '''
    data = {
        'email' : 'jenniferjareau@testemail.com',
        'password' : 'testpassword1253',
        'name_first' : 'jennifer', 
        'name_last' : 'jareau',
    }
    resp = requests.post(config.url + 'auth/register/v2', json=data)
    return resp.json()


@pytest.fixture
def dm_set_up():
    '''
    Sets up dm with registered users
    '''
    user1 = register_user(config.url + 'auth/register/v2', 'jenniferjareau@testemail.com', 'testpassworkdas12', 'jennifer', 'jareau')
    user2 = register_user(config.url + 'auth/register/v2', 'emilyprentiss@testemail.com', 'testpassworkdas14', 'emily', 'prentiss')
    user3 = register_user(config.url + 'auth/register/v2', 'penelopegarcia@testemail.com', 'testpassworkdas14456', 'penelope', 'garcia')

    dm1 = create_dm(config.url + 'dm/create/v1', user1.get('token'), [user2.get('auth_user_id'), user3.get('auth_user_id')])

    return user1, user2, user3, dm1

@pytest.fixture
def channel_set_up():
    '''
    Sets up channels with registered users
    '''
    user1 = register_user(config.url + 'auth/register/v2', 'jenniferjareau@testemail.com', 'testpassworkdas12', 'jennifer', 'jareau')
    user2 = register_user(config.url + 'auth/register/v2', 'emilyprentiss@testemail.com', 'testpassworkdas14', 'emily', 'prentiss')
    user3 = register_user(config.url + 'auth/register/v2', 'penelopegarcia@testemail.com', 'testpassworkdas14', 'penelope', 'garcia')

    channel1 = channels_create(config.url + 'channels/create/v2', user1.get('token'), 'motherland', True)
    channel2 = channels_create(config.url + 'channels/create/v2', user1.get('token'), 'cession', True)

    channel_invite(config.url + 'channel/invite/v2', user1.get('token'), channel1.get('channel_id'), user3.get('auth_user_id'))
    
    add_owner(config.url + 'channel/addowner/v1', user1.get('token'), channel1.get('channel_id'), user2.get('auth_user_id'))
    return user1, user2, user3, channel1, channel2

@pytest.fixture
def message_chan_setup():
    '''
    Sets up channels and registered users with messages sent in the channel
    '''
    user1 = register_user(config.url + 'auth/register/v2', 'jenniferjareau@testemail.com', 'testpassworkdas12', 'jennifer', 'jareau')
    user2 = register_user(config.url + 'auth/register/v2', 'emilyprentiss@testemail.com', 'testpassworkdas14', 'emily', 'prentiss')
    user3 = register_user(config.url + 'auth/register/v2', 'penelopegarcia@testemail.com', 'testpassworkdas14', 'penelope', 'garcia')

    channel1 = channels_create(config.url + 'channels/create/v2', user1.get('token'), 'motherland', True)

    channel_invite(config.url + 'channel/invite/v2', user1.get('token'), channel1.get('channel_id'), user3.get('auth_user_id'))
    channel_join(config.url + 'channel/join/v2', user3.get('token'), channel1.get('channel_id'))
    
    add_owner(config.url + 'channel/addowner/v1', user1.get('token'), channel1.get('channel_id'), user2.get('auth_user_id'))
    
    string = 'hello there world this is a test to test that this works'
    message_list = string.split()
    msgs = []
    for i in range(len(message_list)):
        msgs.append(message_send(config.url + 'message/send/v2', user1.get('token'), channel1.get('channel_id'), message_list[i]))
    
    return user1, user2, user3, channel1, msgs


@pytest.fixture
def message_dm_setup():
    '''
    Sets up registered users and dm with messages sent in the dm
    '''
    user1 = register_user(config.url + 'auth/register/v2', 'jenniferjareau@testemail.com', 'testpassworkdas12', 'jennifer', 'jareau')
    user2 = register_user(config.url + 'auth/register/v2', 'emilyprentiss@testemail.com', 'testpassworkdas14', 'emily', 'prentiss')
    user3 = register_user(config.url + 'auth/register/v2', 'penelopegarcia@testemail.com', 'testpassworkdas14', 'penelope', 'garcia')

    dm1 = create_dm(config.url + 'dm/create/v1', user1.get('token'), [user2.get('auth_user_id'), user3.get('auth_user_id')])

    string = 'hello there world this is a test to test that this works'
    message_list = string.split()
    msgs = []
    for i in range(len(message_list)):
        msgs.append(dm_message_send(config.url + 'message/senddm/v1', user1.get('token'), dm1.get('dm_id'), message_list[i]))
        
    return user1, user2, user3, dm1, msgs

