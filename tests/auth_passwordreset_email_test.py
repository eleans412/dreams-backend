from tests.fixture import channel_set_up, auth_set_up
from src.auth import auth_passwordreset_request_v1
from src.error import AccessError, InputError
from src.data import getData
import pytest

"""
Will check that the email sent is a valid email and send a reset code to the user to change their password

Arguments:
    email (str) - the email that belongs to the user

Exceptions:
    N/A

Returns:
    None
"""

data = getData()

def test_functionality(auth_set_up):
    change_valid = False

    # Save the existing password to confirm the password has been modified in the reset request
    for user in data['users']:
        if user.get('auth_user_id') == auth_set_up[0].get('auth_user_id'):
            email = user.get('email')
    # Call reset password
    auth_passwordreset_request_v1(email)
    
    # Check that there has been a change in the password in the data structure
    for user in data['users']:
        if user.get('auth_user_id') == auth_set_up[0].get('auth_user_id'):
            # if the password is not the same as it was before reset was called
            # then the reset password functionality has worked sucessfully
            if user['reset_code']:
                change_valid = True

    assert change_valid

def test_invalid_email():
    with pytest.raises(InputError):
        auth_passwordreset_request_v1('hi there')


def test_no_email():
    with pytest.raises(InputError):
        auth_passwordreset_request_v1(None)
