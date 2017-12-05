import json
import pycurl
import StringIO
import urllib
import random
import time
import decimal

from oauth_secret import oauth_token
from wrt_dynamodb_handler import *
from wrt_lists import *
from wrt_respond import *


def handle_agenda_command(user, user_name, text, team_domain):
    if text == "":
        return get_all_agenda_items(False)
    elif text == "all" and user == 'U2W19KS75':
        return get_all_agenda_items(True)
    elif text == "clear":
        return clear_user_items(user_name)
    elif text == "clearall" and (user == 'U2W19KS75' or user == 'U0F29H1L0'):
        return clear_all_items()
    elif text.startswith("remove") and len(text.split(' ')) == 2 and text.split(' ')[1].isdigit():
		return delete_item_by_index(user, user_name, int(text.split(' ')[1]) - 1)
    else:
        return put_item_in_agenda(text, user_name)

def clear_all_items():
    items = get_weekly_items()
    items_to_delete = {}
    for i in items:
        items_to_delete[i['pri']] = i['agenda']
    if len(items_to_delete) > 0:
        deleted = delete_items_by_key(items_to_delete, "WRT_agenda", "pri", "agenda")
        return respond(None, "deleted %s items" % deleted)
    else:
        return respond(None, "no items to delete")
        
def clear_user_items(user_name):
    items = get_weekly_items()
    items_to_delete = {}
    for i in items:
        if i['agenda'].endswith('(' + user_name + ')') and not i['agenda'].startswith('[deleted]'):
            items_to_delete[i['pri']] = i['agenda']
    if len(items_to_delete) > 0:
        deleted = delete_items_by_key(items_to_delete, "WRT_agenda", "pri", "agenda")
        return respond(None, "deleted %s items" % deleted)
    else:
        return respond(None, "you have no items, so none were deleted")

def delete_item_by_index(user, user_name, index):
    items = get_weekly_items()
    items_map = {}
    for i in items:
        items_map[i['pri']] = i['agenda']
        
    if index < 0 or index >= len(sorted(items_map.iterkeys())):
        return respond(None, "index out of range")
    key = sorted(items_map.iterkeys())[index]
    if not items_map[key].endswith('(' + user_name + ')'):
        return respond(None, "That item doesn't belong to you")
    deleted = delete_items_by_key({key: items_map[key]}, "WRT_agenda", "pri", "agenda")
    return respond(None, "deleted %s items" % deleted)

def put_item_in_agenda(text, user_name):
    item = text + ' (' + user_name + ')' #attach user name to agenda items
    created_at = decimal.Decimal(time.time())
    Item = { 
        'pri': created_at,
        'created_at' : created_at,
        'agenda' : item
    }
    put_item_in_table(Item, "WRT_agenda")
    
    return respond(None, "added: " + item)
    
def get_weekly_items():
    end_time = decimal.Decimal(time.time())
    start_time = decimal.Decimal(end_time - 604800) #that many seconds in a week
    filter_object = lambda x: x['created_at'] > start_time
    return get_items_from_table('WRT_agenda', filter_object, 'agenda')

def get_all_agenda_items(admin):
    response = get_weekly_items()
    items = {}
    for i in response:
        items[str(float(i['created_at']))] = i['agenda'].strip('"')
    
    sorted_items = []
    for i in sorted(items.iterkeys()):
        sorted_items.append(items[i])
    if len(sorted_items) == 0:
        return respond(None, "there are no agenda items")
    return_string = "Here are your agenda items:"
    for i in range(len(sorted_items)):
        return_string += "\n%i. %s" % (i + 1, sorted_items[i])
    
    return respond(None, return_string)


def post_the_agenda():
    message = get_all_agenda_items(False)['text']
    message += "\n\n React with a " + random.choice(agenda_react_emojis) + " if you're coming"
    post_to_channel(message)

channel_id='C07MWEYPR'
def post_to_channel(message):
    c = pycurl.Curl()
    url = 'https://waterloorocketry.slack.com/api/chat.postMessage?token=' + \
        oauth_token + '&channel=' + channel_id + '&text=' + urllib.quote_plus(message)
    url = url.decode('utf-8').encode('ascii')
    c.setopt(c.URL, url)
    buffer = StringIO.StringIO()
    c.setopt(c.WRITEFUNCTION, buffer.write)
    c.perform()
    c.close()
    json_data = json.loads(buffer.getvalue())
    if 'ok' in json_data and json_data['ok']:
        return respond(None, "yep. Posted a thing.")
    return respond(None, "something failed. You figure it out: " + str(json_data))
