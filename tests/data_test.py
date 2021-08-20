from src.data import saveAndReturn
from src.other import clear_v1
from src.auth import auth_register_v2
from tests.fixture import auth_set_up

def test_functionality(auth_set_up):
    """
    Test ability to create and store data as intended

    Parameters:
        - auth_set_up (fixture)

    Exceptions:
        - N/A

    Return:
        - None
    """

    response = saveAndReturn(auth_set_up[0])

    key_list = []
    key_list = response.split()
    # Split the string and input it into a list to access specific keys in the response
    # Check that the auth_user_id is 1
    assert key_list[1] == '1,'