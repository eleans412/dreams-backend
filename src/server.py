import sys
from json import dumps, loads 
from flask import Flask, request
from flask_cors import CORS
from src.error import InputError
from src import config
from src.data import saveAndReturn, getData
import src.auth
import src.other
import src.channels
import src.channel
import src.admin
import src.user
import src.users
import src.dm
import src.timer
import _thread
import src.message
import src.standup

#After the server starts, we read from the file to get the most recent data stored

def defaultHandler(err):
    response = err.get_response()
    print('response', err, err.get_response())
    response.data = dumps({
        "code": err.code,
        "name": "System Error",
        "message": err.get_description(),
    })
    response.content_type = 'application/json'
    return response

APP = Flask(__name__)
CORS(APP)

APP.config['TRAP_HTTP_EXCEPTIONS'] = True
APP.register_error_handler(Exception, defaultHandler)

# Example
@APP.route("/echo", methods=['GET'])
def echo():
    data = request.args.get('data')
    if data == 'echo':
   	    raise InputError(description='Cannot echo "echo"')
    return dumps({
        'data': data
    })

try: 
    with open('database.json', 'r') as file:
        data = loads(file.read())
except: 
    data = {}

# Auth routes
# =====================================================
@APP.route("/auth/login/v2", methods=['POST'])
def auth_login_wrapper():
    info = request.get_json()
    return saveAndReturn(src.auth.auth_login_v2(info['email'], info['password']))

@APP.route("/auth/register/v2", methods=['POST'])
def auth_register_wrapper():
    data = request.get_json()
    registered_user = src.auth.auth_register_v2(data['email'], data['password'], data['name_first'], data['name_last'])
    return saveAndReturn(registered_user)

@APP.route("/auth/logout/v1", methods=['POST'])
def auth_logout_wrapper():
    data = request.get_json()
    return saveAndReturn(src.auth.auth_logout_v1(data['token']))

@APP.route("/auth/passwordreset/request/v1", methods=['POST'])
def password_reset_request_wrapper():
    data = request.get_json()
    return saveAndReturn(src.auth.auth_passwordreset_request_v1(data['email']))


@APP.route("/auth/passwordreset/reset/v1", methods=['POST'])
def passoword_reset_wrapper():
    data = request.get_json()
    return saveAndReturn(src.auth.auth_passwordreset_reset_v1(data['reset_code'], data['new_password']))


# Channel routes
# =====================================================
@APP.route("/channel/invite/v2", methods=['POST'])
def channel_invite_wrapper():
    data = request.get_json()
    return saveAndReturn(src.channel.channel_invite_v2(data['token'], data['channel_id'], data['u_id']))

@APP.route("/channel/details/v2", methods=['GET'])
def channel_details_wrapper():
    token = request.args.get('token')
    channel_id = request.args.get('channel_id')
    return saveAndReturn(src.channel.channel_details_v2(token, channel_id))

@APP.route("/channel/messages/v2", methods=['GET'])
def channel_messages_wrapper():
    token = request.args.get('token')
    channel_id = request.args.get('channel_id')
    start = request.args.get('start')
    return saveAndReturn(src.channel.channel_messages_v2(token, channel_id, start))

@APP.route("/channel/join/v2", methods=['POST'])
def channel_join_wrapper():
    data = request.get_json()
    return saveAndReturn(src.channel.channel_join_v2(data['token'], data['channel_id']))

@APP.route("/channel/addowner/v1", methods=['POST'])
def channel_addowner_wrapper():
    data = request.get_json()
    return saveAndReturn(src.channel.channel_addowner_v1(data['token'], data['channel_id'], data['u_id']))


@APP.route("/channel/removeowner/v1", methods=['POST'])
def channel_removeowner_wrapper():
    data = request.get_json()
    return saveAndReturn(src.channel.channel_removeowner_v1(data['token'], data['channel_id'], data['u_id']))


@APP.route("/channel/leave/v1", methods=['POST'])
def channel_leave_wrapper():
    data = request.get_json()
    return saveAndReturn(src.channel.channel_leave_v1(data['token'], data['channel_id']))

# Channels routes
# =====================================================
@APP.route("/channels/list/v2", methods=['GET'])
def channels_list_wrapper():
    token = request.args.get('token')
    return saveAndReturn(src.channels.channels_list_v2(token))

@APP.route("/channels/listall/v2", methods=['GET'])
def channels_listall_wrapper():
    token = request.args.get('token')
    return saveAndReturn(src.channels.channels_listall_v2(token))

@APP.route("/channels/create/v2", methods=['POST'])
def channels_create_wrapper():
    data = request.get_json()
    return saveAndReturn(src.channels.channels_create_v2(data['token'], data['name'], data['is_public']))

# Message routes
# =====================================================
@APP.route("/message/send/v2", methods=['POST'])
def message_send_wrapper():
    data = request.get_json()
    return saveAndReturn(src.message.message_send_v2(data['token'], data['channel_id'], data['message']))

@APP.route("/message/edit/v2", methods=['PUT'])
def message_edit_wrapper():
    data = request.get_json()
    return saveAndReturn(src.message.message_edit_v2(data['token'], data['message_id'], data['message']))

@APP.route("/message/remove/v1", methods=['DELETE'])
def message_remove_wrapper():
    data = request.get_json()
    return saveAndReturn(src.message.message_remove_v1(data['token'], data['message_id']))

@APP.route("/message/share/v1", methods=['POST'])
def message_share_wrapper():
    data = request.get_json()
    return saveAndReturn(src.message.message_share_v1(data['token'], data['og_message_id'], data['message'], data['channel_id'], data['dm_id']))

@APP.route("/message/senddm/v1", methods=['POST'])
def message_senddm_wrapper():
    data = request.get_json()
    return saveAndReturn(src.message.message_senddm_v1(data['token'], data['dm_id'], data['message']))

@APP.route("/message/react/v1", methods=['POST'])
def message_react_wrapper():
    data = request.get_json()
    return saveAndReturn(src.message.message_react_v1(data['token'], data['message_id'], data['react_id']))

@APP.route("/message/sendlater/v1", methods=['POST'])
def message_sendlater_wrapper():
    data = request.get_json()
    return saveAndReturn(src.message.message_sendlater_v1(data['token'], data['channel_id'], data['message'], data['time_sent']))

@APP.route("/message/sendlaterdm/v1", methods=['POST'])
def message_sendlaterdm_wrapper():
    data = request.get_json()
    return saveAndReturn(src.message.message_sendlaterdm_v1(data['token'], data['dm_id'], data['message'], data['time_sent']))

@APP.route("/message/unreact/v1", methods=['POST'])
def message_unreact_wrapper():
    data = request.get_json()
    return saveAndReturn(src.message.message_unreact_v1(data['token'], data['message_id'], data['react_id']))

@APP.route("/message/pin/v1", methods=['POST'])
def message_pin_wrapper():
    data = request.get_json()
    return saveAndReturn(src.message.message_pin_v1(data['token'], data['message_id']))


@APP.route("/message/unpin/v1", methods=['POST'])
def message_unpin_wrapper():
    data = request.get_json()
    return saveAndReturn(src.message.message_unpin_v1(data['token'], data['message_id']))


# Dm routes
# =====================================================
@APP.route("/dm/details/v1", methods=['GET'])
def dm_details_wrapper():
    token = request.args.get('token')
    dm_id = request.args.get('dm_id')
    return dumps(src.dm.dm_details_v1(token, dm_id))

@APP.route("/dm/list/v1", methods=['GET'])
def dm_list_wrapper():
    token = request.args.get('token')
    return dumps(src.dm.dm_list_v1(token))

@APP.route("/dm/create/v1", methods=['POST'])
def dm_create_wrapper():
    data = request.get_json()
    return dumps(src.dm.dm_create_v1(data['token'], data['u_ids']))

@APP.route("/dm/remove/v1", methods=['DELETE'])
def dm_remove_wrapper():
    data = request.get_json()
    return dumps(src.dm.dm_remove_v1(data['token'], data['dm_id']))

@APP.route("/dm/invite/v1", methods=['POST'])
def dm_invite_wrapper(): 
    data = request.get_json()
    return dumps(src.dm.dm_invite_v1(data['token'], data['dm_id'], data['u_id']))

@APP.route("/dm/leave/v1", methods=['POST'])
def dm_leave_wrapper():
    data = request.get_json()
    return saveAndReturn(src.dm.dm_leave_v1(data['token'], data['dm_id']))

@APP.route("/dm/messages/v1", methods=['GET'])
def dm_messages_wrapper():
    token = request.args.get('token')
    dm_id = request.args.get('dm_id')
    start = request.args.get('start')
    return saveAndReturn(src.dm.dm_messages_v1(token, dm_id, start))

# Admin routes
# =====================================================
@APP.route("/admin/user/remove/v1", methods=['DELETE'])
def user_remove_wrapper():
    data = request.get_json()
    return saveAndReturn(src.admin.admin_user_remove_v1(data['token'], data['u_id']))

@APP.route("/admin/userpermission/change/v1", methods=['POST'])
def user_permissions_wrapper():
    data = request.get_json()
    return saveAndReturn(src.admin.admin_userpermissions_change_v1(data['token'], data['u_id'], data['permission_id']))
    

# User routes
# =====================================================
@APP.route("/user/profile/v2", methods=['GET'])
def user_profile_wrapper():
    token = request.args.get('token')
    u_id = request.args.get('u_id')
    return saveAndReturn(src.user.user_profile_v2(token, u_id))
    
@APP.route("/user/profile/setname/v2", methods=['PUT'])
def user_setname_wrapper():
    data = request.get_json()
    return saveAndReturn(src.user.user_profile_setname_v2(data['token'], data['name_first'], data['name_last']))

@APP.route("/user/profile/setemail/v2", methods=['PUT'])
def user_setemail_wrapper():
    data = request.get_json()
    return saveAndReturn(src.user.user_profile_setemail_v2(data['token'], data['email']))


@APP.route("/user/profile/sethandle/v1", methods=['PUT'])
def user_sethandle_wrapper():
    data = request.get_json()
    return saveAndReturn(src.user.user_profile_sethandle_v1(data['token'], data['handle_str']))

@APP.route("/user/stats/v1", methods=['GET'])
def user_stats_wrapper():
    token = request.args.get('token')
    return saveAndReturn(src.user.user_stats_v1(token))


@APP.route("/user/profile/uploadphoto/v1", methods=['POST'])
def user_profile_pic_wrapper():
    data = request.get_json()
    return saveAndReturn(src.user.user_profile_uploadphoto_v1(data['token'], data['img_url'], data['x_start'], data['y_start'], data['x_end'], data['y_end']))



# Users routes
# ===========================================================

@APP.route("/users/all/v1", methods=['GET'])
def users_all_wrapper():
    token = request.args.get('token')
    return saveAndReturn(src.users.users_all_v1(token))

@APP.route("/users/stats/v1", methods=['GET'])
def users_stats_wrapper():
    token = request.args.get('token')
    return saveAndReturn(src.users.users_stats_v1(token))

# Standup routes
# ===========================================================
@APP.route("/standup/start/v1", methods=['POST'])
def standup_start_wrapper():
    data = request.get_json()
    return saveAndReturn(src.standup.standup_start_v1(data['token'], data['channel_id'], data['length']))

@APP.route("/standup/active/v1", methods=['GET'])
def standup_active_wrapper():
    token = request.args.get('token')
    channel_id = request.args.get('channel_id')
    return saveAndReturn(src.standup.standup_active_v1(token, channel_id))

@APP.route("/standup/send/v1", methods=['POST'])
def standup_send_wrapper():
    data = request.get_json()
    return saveAndReturn(src.standup.standup_send_v1(data['token'], data['channel_id'], data['message']))


# Other routes
# ===========================================================
@APP.route("/notifications/get/v1", methods=['GET'])
def get_notifications_wrapper():
    token = request.args.get('token')
    # Check that this is the file notificaitons is in 
    return saveAndReturn(src.message.notifications_get_v1(token))

@APP.route("/search/v2", methods=['GET'])
def search_wrapper():
    token = request.args.get('token')
    query_str = request.args.get('query_str')
    return saveAndReturn(src.other.search_v2(token, query_str))

@APP.route('/clear/v1', methods=['DELETE'])
# Try not to call these the same as the functions you already have because that might lead to clashes
def clear_wrapper():
    clear_data = src.other.clear_v1()
    return saveAndReturn(clear_data)

if __name__ == "__main__":
    _thread.start_new_thread(src.timer.timer, ())
    APP.run(port=config.port) # Do not edit this port
