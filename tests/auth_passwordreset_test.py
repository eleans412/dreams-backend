from src.auth import auth_passwordreset_reset_v1, auth_passwordreset_request_v1
from tests.fixture import auth_set_up
from src.error import AccessError, InputError
from src.helper import hash
from src.data import getData
import pytest

'''
Given a reset code for a user, set that user's new password to the password provided

Arguments:
    reset_code (str) - the code that the user receives in their email
    new_password (str) - the password that the user wants to reset their password to

Exceptions:
    InputError - reset_code is not a valid reset code
    InputError - Password entered is less than 6 characters long

Return Value:
    None
'''

data = getData()

def test_functionality(auth_set_up):
    change_valid = False
    new_password = 'Ilikebananas12'
    check_password = hash(new_password)
    reset_code = '445826913reset'

    # Which one? second one seems to make the most sense if the reset code is going to be randomly generated, but is it too hardcodey?
    # Get an email to reset the user's password
    auth_passwordreset_request_v1(data['users'][auth_set_up[0].get('auth_user_id') - 1].get('email'))

    # Set the reset code for the user to check that the code check is happening as expected
    data['users'][auth_set_up[0].get('auth_user_id') - 1]['reset_code'] = '445826913reset'
    
    auth_passwordreset_reset_v1(reset_code, new_password)

    if data['users'][auth_set_up[0].get('auth_user_id') - 1]['password'] is not check_password:
        change_valid = True
    
    assert change_valid

def test_reset_code_invalid():
    with pytest.raises(InputError):
        auth_passwordreset_reset_v1('Nottheresetcode', '12345')

def test_empty_reset_code():
    with pytest.raises(InputError):
        auth_passwordreset_reset_v1(None, '12345')

def test_password_invalid():
    reset_code = '445826913reset'
    with pytest.raises(InputError):
        auth_passwordreset_reset_v1(reset_code, '12345')

def test_empty_password(auth_set_up):  

    # Set the reset code for the user to check that the code check is happening as expected
    data['users'][auth_set_up[0].get('auth_user_id') - 1]['password'] = '445826913reset'
    
    with pytest.raises(InputError):
        auth_passwordreset_reset_v1('445826913reset', None)
