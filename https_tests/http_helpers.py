import requests
from flask import Flask, request

def register_user(url, email, password, name_first, name_last):
    '''
    A function to abstract away the request process when registering for http tests

    Parameters:
        url (str): the url that the data will be sent to
        email (str) : the email of the user to be registered
        password (str) : the password of the user to be registered
        name_first (str) : the first name of the user to be registered
        name_last (str) : the last name of the user to be registered
    
    Returns:
        The request response in json form
    '''
    json_data = {
        'email' : email,
        'password' : password,
        'name_first' : name_first, 
        'name_last' : name_last,
    }
    response = requests.post(url, json=json_data)
    load = response.json()
    return load

def channels_create(url, token, name, is_public):
    '''
    A function to abstract away the request process when creating channel for http tests

    Parameters:
        url (str): the url that the data will be sent to
        token(str) : the token of the user creating the channel
        name (str): name of the channel to be created
        is_public (bool) : whether the channel is public or private

    Returns:
        The request response in json form
    '''
    json_data = {
        'token' : token,
        'name' : name,
        'is_public' : is_public,
    }
    response = requests.post(url, json=json_data)
    load = response.json()
    return load

def channel_invite(url, token, channel_id, u_id):
    '''
    A function to abstract away the request process when inviting to channels for http tests

    Parameters:
        url (str): the url that the data will be sent to
        token(str) : the token of the user creating the channel
        channel_id (int): the channel the user is invited to
        u_id (int) : the user being invited

    Returns:
        The request response in json form
    '''
    json_data = {
        'token' : token,
        'channel_id' : channel_id,
        'u_id' : u_id,
    }
    response = requests.post(url, json=json_data)
    load = response.json()
    return load

def channel_join(url, token, channel_id):
    '''
    A function to abstract away the request process when joining channels for http tests

    Parameters:
        url (str): the url that the data will be sent to
        token(str) : the user joining the channel
        channel_id (int): the channel the user is joining

    Returns:
        The request response in json form
    '''
    json_data = {
        'token' : token,
        'channel_id' : channel_id,
    }
    response = requests.post(url, json=json_data)
    load = response.json()
    return load


def message_send(url, token, channel_id, message):
    '''
    A function to abstract away the request process when sending messages for http tests

    Parameters:
        url (str): the url that the data will be sent to
        token(str) : the user sending the message
        channel_id (int): the channel the message will be sent to
        message (str): the message being sent

    Returns:
        The request response in json form
    '''
    message_data = {'token' : token, 'channel_id' : channel_id, 'message' : message}
    
    response = requests.post(url, json=message_data)
    load = response.json()
    return load

def dm_message_send(url, token, dm_id, message):
    '''
    A function to abstract away the request process when sending dm messages for http tests

    Parameters:
        url (str): the url that the data will be sent to
        token(str) : the user sending the message
        dm_id (int): where the message will be sent
        message (str) : the message being sent

    Returns:
        The request response in json form
    '''
    message_data = {'token' : token, 'dm_id' : dm_id, 'message' : message}
    response = requests.post(url, json=message_data)
    load = response.json()
    return load

def create_dm(url, token, u_ids):
    '''
    A function to abstract away the request process when joining channels for http tests

    Parameters:
        url (str): the url that the data will be sent to
        token(str) : the user creating the dm
        u_ids (int) : list of the u_id's that will be a part of this dm

    Returns:
        The request response in json form
    '''
    data = {
        'token' : token,
        'u_ids' : u_ids
    }
    response = requests.post(url, json=data)
    load = response.json()
    return load

def add_owner(url, token, channel_id, u_id):
    '''
    A function to abstract away the request process to add owner to channel for http tests

    Parameters:
        url (str): the url that the data will be sent to
        token(str) : the user adding another user as owner
        channel_id (int): the channel to add the owner to
        u_id (int): the user being added as owner

    Returns:
        The request response in json form
    '''
    data = {
        'token': token, 
        'channel_id' : channel_id, 
        'u_id': u_id
    }
    response = requests.post(url, json=data)
    load = response.json()
    return load
