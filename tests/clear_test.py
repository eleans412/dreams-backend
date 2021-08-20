from src.data import getData
from src.auth import auth_register_v2
from src.channels import channels_create_v2
from src.message import message_send_v2
from src.other import clear_v1
import pytest

def test_clear():
    """
    Resets the internal data of the application to it's initial state

    Parameters:
    - None

    Exceptions:
    - N/A

    Return Type:
    - None
    """

    #test functionality of clear with an extra long string

    user = auth_register_v2('kimseeto@testemail.com', 'password5467', 'kim', 'seeto')

    testchannel = channels_create_v2(user['token'], 'new_channel', True)

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
        message_send_v2(user['token'], testchannel['channel_id'], message)

    clear_v1()
    data = getData()
    assert data == {}