import boto3
import json
import logging
import os
import pycurl
import StringIO
import urllib
import random
import time
import decimal
from oauth.py import oauth_token

from base64 import b64decode
from urlparse import parse_qs


logger = logging.getLogger()
logger.setLevel(logging.INFO)

DEBUG_LIST = ["2W19KS75"]
BAY_STATUS_LIST = [ "making the bay great again",
                    "adding to the clutter",
                    "doing stuff and things and such",
                    "avoiding assignments",
                    "making the norse god vidar proud",
                    "why don't I have 40 apple interviews yet?",
                    "Not eating",
                    "Sleeping in the comfy leather chair thing",
                    "juggling ignition spacers",
                    "what if we stored all of our fill hoses in a linked list?",
                    ":rocket::rocket::rocket::rocket::rocket::rocket::rocket::rocket::rocket::rocket:",
                    "knolling",
                    "soldering dangerously"]
BAY_LEAVE_STATUS_LIST = ["went home",
                "not in the bay anymore",
                "doing homework or reddit or something",
                "off having adventures and slaying dragons",
                "in the bay only in spirit",
                "oh right, I still have classes",
                "struggling to explain to normies why I spend so much time at rocketry",
                "stripping for money to buy better wire strippers",
                "praying for successful ignition",
                "moved to iceland. Became a shepherd."]
BAY_LEAVE_EMOJI_LIST = [":feelsbadman:",
                        ":rip:",
                        ":sob:",
                        ":robin:"]


def respond(err, res=None):
    return {
        'statusCode': '400' if err else '200',
        'text': err.message if err else res,
        'headers': {
            'Content-Type': 'application/json',
        },
    }


def lambda_handler(event, context):
    try:
        params = parse_qs(event['body'])
        user = params['user_id'][0]
        command = params['command'][0]
        team_domain = params['team_domain'][0]
    except:
        return post_the_agenda()
    
    if command == '/bay':
        return handle_bay_command(event, context, params, user, team_domain)
    elif command == '/agenda':
        return handle_agenda_command(event, context, params, user, team_domain)
    elif command == '/todo':
        return handle_todo_command(event, context, params, user, team_domain)
    elif command == 'postit':
        return post_the_agenda()
    else:
        return respond(None, "unknown command")
        
#todo list stuff
def handle_todo_command(event, context, params, user, team_domain):
    text = ""
    if 'text' in params:
        text = params['text'][0]
    if text == "":
        return get_all_todo_items_pretty(user)
    elif text == "clear":
        return clear_todo_items(user)
    elif text.startswith("remove") and len(text.split(' ')) == 2 and text.split(' ')[1].isdigit():
        return delete_todo_by_index(user, int(text.split(' ')[1]) - 1)
    else:
        return add_todo_item(user, text)

def get_all_todo_items_pretty(user):
    response = get_all_todo_items(user)

    count = response['Count']
    
    items = {}
    for i in range(count):
        items[str(float(response['Items'][i]['time_added']))] = response['Items'][i]['todo_item'].strip('"')
    
    sorted_items = []
    for i in sorted(items.iterkeys()):
        if items[i].startswith('[deleted]'):
            continue
        sorted_items.append(items[i])
    if len(sorted_items) == 0:
        return respond(None, "You currently have no issues assigned to you. Enjoy your day!")
    return_string = "Here are your todo items:"
    for i in range(len(sorted_items)):
        return_string += "\n%i. %s" % (i + 1, sorted_items[i])
    
    return respond(None, return_string)

def get_all_todo_items(user):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('WRT_todo')

    return table.scan(
        Select = 'ALL_ATTRIBUTES',
        FilterExpression = boto3.dynamodb.conditions.Attr('User_ID').eq(user))

def clear_todo_items(user):
    items = get_all_todo_items(user)
    items_to_delete = {}
    for i in range(items['Count']):
        items_to_delete[items['Items'][i]['time_added']] = items['Items'][i]['todo_item']
    if len(items_to_delete) > 0:
        return delete_todo_by_key(items_to_delete)
    return respond(None, "no todo items to delete")

def delete_todo_by_key(items):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('WRT_todo')
    items_deleted = len(items)
    for i in items:
        primary = sorted(items.iterkeys())[0]
        text = items[i]
        if text.startswith('[deleted]'):
            items_deleted -= 1
            continue
        response = table.update_item(
            Key = {
                'time_added' : i
            },
            UpdateExpression = 'SET todo_item = :t',
            ExpressionAttributeValues = {
                ':t' : '[deleted] ' + text
            }
        )
    return respond(None, "deleted %s items" % items_deleted)

def delete_todo_by_index(user, index):
    items = get_all_todo_items(user)
    items_map = {}
    for i in range(items['Count']):
        if items['Items'][i]['todo_item'].startswith('[deleted]'):
            continue
        items_map[items['Items'][i]['time_added']] = items['Items'][i]['todo_item']
        
    if index < 0 or index >= len(sorted(items_map.iterkeys())):
        return respond(None, "index out of range")
    key = sorted(items_map.iterkeys())[index]
    return delete_todo_by_key({key: items_map[key]})

def add_todo_item(user, text):
    item = text
    time_added = decimal.Decimal(time.time())
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('WRT_todo')
    table.put_item(
        Item = { 
            'time_added': time_added,
            'todo_item' : item,
            'User_ID' : user
        })
    
    return respond(None, "added: " + item)
        
#agenda stuff
def handle_agenda_command(event, context, params, user, team_domain):
    user_name = params['user_name'][0]
    text = ""
    if 'text' in params:
        text = params['text'][0]
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
    for i in range(items['Count']):
        items_to_delete[items['Items'][i]['pri']] = items['Items'][i]['agenda']
    if len(items_to_delete) > 0:
        return delete_items_by_key(items_to_delete)
    else:
        return respond(None, "no items to delete")
        
def clear_user_items(user_name):
    items = get_weekly_items()
    items_to_delete = {}
    for i in range(items['Count']):
        if items['Items'][i]['agenda'].endswith('(' + user_name + ')') and not items['Items'][i]['agenda'].startswith('[deleted]'):
            items_to_delete[items['Items'][i]['pri']] = items['Items'][i]['agenda']
    if len(items_to_delete) > 0:
        return delete_items_by_key(items_to_delete)
    else:
        return respond(None, "you have no items, so none were deleted")
    return respond(None, str(items_to_delete))

def delete_items_by_key(items):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('WRT_agenda')
    items_deleted = len(items)
    for i in items:
        primary = sorted(items.iterkeys())[0]
        text = items[i ]
        if text.startswith('[deleted]'):
            items_deleted -= 1
            continue
        response = table.update_item(
            Key = {
                'pri' : i
            },
            AttributeUpdates = {
                'agenda' : {
                    'Value' : str('[deleted] ' + text),
                    'Action' : 'PUT'
                }
            }
        )
    return respond(None, "deleted %s items" % items_deleted)

def delete_item_by_index(user, user_name, index):
    items = get_weekly_items()
    items_map = {}
    for i in range(items['Count']):
        if items['Items'][i]['agenda'].startswith('[deleted]'):
            continue
        items_map[items['Items'][i]['pri']] = items['Items'][i]['agenda']
        
    if index < 0 or index >= len(sorted(items_map.iterkeys())):
        return respond(None, "index out of range")
    key = sorted(items_map.iterkeys())[index]
    if not items_map[key].endswith('(' + user_name + ')'):
        return respond(None, "That item doesn't belong to you")
    return delete_items_by_key({key: items_map[key]})

def put_item_in_agenda(text, user_name):
    
    item = text + ' (' + user_name + ')' #attach user name to agenda items
    created_at = decimal.Decimal(time.time())
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('WRT_agenda')
    table.put_item(
        Item = { 
            'pri': created_at,
            'created_at' : created_at,
            'agenda' : item
        })
    
    return respond(None, "added: " + item)
    
def get_weekly_items():
    end_time = decimal.Decimal(time.time())
    start_time = decimal.Decimal(end_time - 604800) #that many seconds in a week
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('WRT_agenda')
    
    return table.scan(
        Select = 'ALL_ATTRIBUTES',
        FilterExpression = boto3.dynamodb.conditions.Attr('created_at').between(start_time,end_time)
        )

def get_all_agenda_items(admin):
    response = get_weekly_items()

    count = response['Count']
    
    items = {}
    for i in range(count):
        items[str(float(response['Items'][i]['created_at']))] = response['Items'][i]['agenda'].strip('"')
    
    sorted_items = []
    for i in sorted(items.iterkeys()):
        if items[i].startswith('[deleted]') and not admin:
            continue
        sorted_items.append(items[i])
    if len(sorted_items) == 0:
        return respond(None, "there are no agenda items")
    return_string = "Here are your agenda items:"
    for i in range(len(sorted_items)):
        return_string += "\n%i. %s" % (i + 1, sorted_items[i])
    
    return respond(None, return_string)

agenda_react_emojis = [":acetone:", ":actually_ham:", ":adam:", ":addreaction:", ":alex:", ":alsoham:", ":anarchist:", ":aristotle:", ":axe:", ":banan:", 
                        ":beret:", ":blackspace:", ":bone_ana:", ":broom:", ":chill:", ":cinnamon:", ":comrade:", ":cosin:", ":cute:", ":cuter:", ":cutest:", 
                        ":dab:", ":damn:", ":david:", ":diode:", ":doris:", ":dragoncurve:", ":drill:", ":em:", ":em1:", ":em2:", ":em3:", ":em4:", ":emily:", 
                        ":failfish:", ":feelsbadman:", ":fox:", ":fpaacs:", ":gain:", ":god:", ":gold:", ":goodstuff:", ":goose:", ":greatstuff:", ":ham:", 
                        ":hellothere:", ":hilbert:", ":hilbertcurve:", ":hilberto:", ":hilly:", ":hotstrippers:", ":hussein:", ":infinity:", ":jacob:", ":julia:", 
                        ":kappa:", ":kenneth:", ":koch:", ":lad:", ":lambda:", ":logo:", ":logo2:", ":mandelbrot:", ":mandelbrotrainbow:", ":matrix:", ":maxq:", 
                        ":maxrobin:", ":mcteerts:", ":menger:", ":meowth:", ":miranda:", ":monkas:", ":newhire:", ":nick:", ":nina:", ":ninasback:", ":nofrills:", 
                        ":noosejs:", ":nugget:", ":nylon:", ":ohgod:", ":opvote:", ":pain:", ":parrot:", ":partyparrot:", ":paylad:", ":pita:", ":pjsalt:", ":pogchamp:", 
                        ":polymethlymethacrylate:", ":praxair:", ":psi:", ":q:", ":rip:", ":robin:", ":ryan:", ":ryerson:", ":sadparrot:", ":sanic:", ":shufflelogo:", ":shufflelogo2:", 
                        ":shuffleparrot:", ":shuffleparrot2:", ":sierpinski:", ":sin:", ":siren:", ":sledge:", ":slowpoke:", ":subtle:", ":syzygy:", ":thonking_foce:", ":tru:", ":trump:", 
                        ":truss:", ":upvote:", ":uwin:", ":vdar1:", ":vdar10:", ":vdar11:", ":vdar12:", ":vdar13:", ":vdar2:", ":vdar3:", ":vdar4:", ":vdar5:", ":vdar6:", 
                        ":vdar7:", ":vdar8:", ":vdar9:", ":vithusan:", ":whitespace:", ":wonk:", ":wow:", ":wreckingball:", ":wtf:", ":wtfdiagram:", ":wutface:", 
                        ":yash:", ":yiqing:", ":zak:"]

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
    
    


#bay stuff
def handle_bay_command(event, context, params, user, team_domain):
    if "text" in params:
        text = params['text'][0]
    else:  
        text = ""
    
    if text == "":
        current_status = get_current_status(user,team_domain)
        if current_status in BAY_LEAVE_STATUS_LIST or current_status == "":
            current_status = random.choice(BAY_STATUS_LIST)
        return respond(None, "%s" % set_current_status(user,team_domain,current_status,':rocket:'))
    elif text == "who":
        list_bay = list_of_people_in_bay(team_domain, True)
        if(len(list_bay) == 0):
            return respond(None, "there's no one in the bay right now")
        elif(len(list_bay) == 1):
            return respond(None, "%s is in the bay" % list_bay[0])
        elif(len(list_bay) == 2):
            return respond(None, "%s and %s are in the bay" % (list_bay[0], list_bay[1]))
        else:
            res_str = ", ".join(list_bay[:-1])
            res_str += ", and " + list_bay[-1] + " are all in the bay"
        return respond(None, res_str)
    elif text == "bay_area_iot":
        list_bay = list_of_people_in_bay(team_domain, False)
        return respond(None, json.dumps(list_bay))
    elif text == "leave":
        status_emoji = random.choice(BAY_LEAVE_EMOJI_LIST);
        status_text = random.choice(BAY_LEAVE_STATUS_LIST)
        return respond(None, "%s" % set_current_status(user,team_domain,status_text,status_emoji))
    else:
        return respond(None, "%s" % set_current_status(user,team_domain,text,':rocket:'))

def get_current_status(user, team_domain):
    c = pycurl.Curl()
    url = 'https://' + team_domain + '.slack.com/api/users.profile.get?token=' + oauth_token + '&user=' + user
    url = url.decode('utf-8').encode('ascii')
    c.setopt(c.URL, url)
    buffer = StringIO.StringIO()
    c.setopt(c.WRITEFUNCTION, buffer.write)
    c.perform()
    c.close()
    return json.loads(buffer.getvalue())['profile']['status_text']
    
def set_current_status(user, team_domain, status_text, status_emoji):
    c = pycurl.Curl()
    url = 'https://' + team_domain + '.slack.com/api/users.profile.set?token=' + oauth_token + '&user=' + user +\
            '&profile=' + urllib.quote_plus('{"status_emoji":"' + status_emoji + '","status_text":"' + status_text + '"}')
    url = url.decode('utf-8').encode('ascii')
    c.setopt(c.URL, url)
    buffer = StringIO.StringIO()
    c.setopt(c.WRITEFUNCTION, buffer.write)
    c.perform()
    c.close()
    json_data = json.loads(buffer.getvalue())
    if user in DEBUG_LIST:
        return json.dumps(json_data)
    if (not "ok" in json_data) or (not json_data["ok"]):
        return "something went wrong, error message: " + json.dumps(json_data["error"])
    return "changed your status to " + status_emoji + " " + status_text
    
    
ignore_list = ['U5P2M60AK'] #Stephan is now ignored
def list_of_people_in_bay(team_domain, human_readable):
    c = pycurl.Curl()
    url = 'https://' + team_domain + '.slack.com/api/users.list?token=' + oauth_token
    url = url.decode('utf-8').encode('ascii')
    c.setopt(c.URL, url)
    buffer = StringIO.StringIO()
    c.setopt(c.WRITEFUNCTION, buffer.write)
    c.perform()
    c.close()
    members = json.loads(buffer.getvalue())['members']
    list_bay = []
    for i in members:
        if (not (i['id'] in ignore_list)) and "profile" in i and "status_emoji" in i['profile'] and i['profile']['status_emoji'] == ':rocket:':
            if(human_readable):
                list_bay.append(i['profile']['real_name'])
            else:
                list_bay.append(i['id'])
    return list_bay
